from __future__ import annotations

import logging
import multiprocessing as mp
import subprocess
import time
from abc import ABC, abstractmethod
from collections import UserList
from pathlib import Path

from ctdam.proc.procedure import Procedure
from ctdam.proc.settings import Configuration

from ctdclient.definitions import (
    CONFIG_PATH,
    TEMPLATE_PATH,
    config,
    event_manager,
)

logger = logging.getLogger(__name__)


class ProcessingList(UserList):
    """Collection of processing workflows."""

    data: list[ProcessingConfig]

    def read_processing_files(self):
        """Fills collection with processing workflows."""
        # reset processing configs
        self.data = []
        for file in CONFIG_PATH.glob("*proc*"):
            try:
                self.data.append(self.create_new_processing_config(file))
            except Exception:
                continue

    def run(self, file: Path | str):
        """
        Runs all active processing workflows.

        Parameters
        ----------
        file: Path | str
            The target file to process
        """
        updated_last_processing_files = []
        for proc_config in self.data:
            if proc_config.active:
                proc_config.run(Path(file))
                proc_config.wait()
                if not proc_config.killed:
                    updated_last_processing_files.append(proc_config.name)

        if len(updated_last_processing_files) > 0:
            config.last_processing_files = updated_last_processing_files
            config.write()
            event_manager.publish(
                "processing_successful", target=Path(file).absolute()
            )

    def cancel(self):
        """Cancels all running processing workflows."""
        for proc_config in self.data:
            if proc_config.active:
                proc_config.cancel()

    def toggle_auto_process(self, new_value: bool | None = None):
        """
        Toggle the automatic processing of new files.

        Parameters
        ----------
        new_value: bool | None
            The value to set auto-processing to
        """
        config.processing["auto_process"] = (
            new_value
            if isinstance(new_value, bool)
            else not config.plotting["auto_process"]
        )

    def toggle_config_activity_state(self, proc_config: ProcessingConfig):
        """
        Sets active state of specific processing workflow.

        Parameters
        ----------
        proc_config: ProcessingConfig
            The processing workflow to toggle

        Returns
        -------
        Whether state has been altered.
        """
        for proc in self.data:
            if proc == proc_config:
                proc.active = not proc.active
                return True
        logger.error(
            f"Could not set active processing: {proc_config.path_to_config}"
        )
        return False

    def create_new_processing_config(self, file: Path) -> ProcessingConfig:
        """
        Assembles new processing workflow.

        Parameters
        ----------
        file: Path
            Path to processing workflow configuration file

        Returns
        -------
        A new ProcessingConfig instance.
        """
        if file.suffix == ".toml":
            return ProcessingProcedure(file)
        else:
            return ProcessingScript(file)

    def get_template(
        self,
        template_path: Path = TEMPLATE_PATH.joinpath(
            "processing_template.toml"
        ),
    ):
        """
        Creates a new processing workflow from template.

        Parameters
        ----------
        template_path: Path
            The file path to the template file

        Returns
        -------
        ProcessingConfig instance of the template.
        """
        if not template_path.exists():
            return None
        template = self.create_new_processing_config(template_path)
        self.data.append(template)
        return template

    def remove_config(self, config: ProcessingConfig):
        """
        Removes processing workflow from collection.

        Parameters
        ----------
        config: ProcessingConfig
            The processing workflow configuration
        """
        self.data.remove(config)
        if config.path_to_config.exists():
            config.path_to_config.unlink()


class ProcessingConfig(ABC):
    """Generic processing workflow."""

    current_config: Path

    def __init__(
        self,
        path_to_config: Path | str,
    ):
        self.update_config(path_to_config)
        self.path_to_config = Path(path_to_config)
        self.name = self.path_to_config.name
        self.active = (
            True
            if self.name in [file for file in config.last_processing_files]
            else False
        )

    def __str__(self) -> str:
        return str(self.path_to_config)

    def __repr__(self) -> str:
        return self.__str__()

    @abstractmethod
    def run(self, file: Path):
        """
        Performs processing logic.

        Parameters
        ----------
        file: Path
            The target file to process
        """
        pass

    @abstractmethod
    def update_config(self, path_to_config: Path | str):
        """
        Updates processing workflow information.

        Parameters
        ----------
        path_to_config: Path | str
            File path to processing workflow configuration
        """
        pass

    @abstractmethod
    def wait(self):
        """Waits for processing workflow to finish."""
        pass

    def cancel(self):
        """Cancels a running processing workflow."""
        self.process.kill()
        self.killed = True


class ProcessingProcedure(ProcessingConfig):
    """Processing workflow from ctdam python package workflows."""

    process: mp.Process

    def __init__(self, path_to_config: Path | str):
        super().__init__(path_to_config)

    def update_config(self, path_to_config: Path | str):
        """
        Updates processing workflow information.

        Parameters
        ----------
        path_to_config: Path | str
            File path to processing workflow configuration
        """
        new_config = Path(path_to_config)
        proc_config = Configuration(new_config)
        self.procedure = Procedure(
            proc_config,
            seabird_exe_directory=config.path_to_proc_exes,
            auto_run=False,
            procedure_fingerprint_directory=config.processing[
                "generate_processing_fingerprint"
            ],
            file_type_dir=config.processing["file_type_dir"],
        )
        self.modules = proc_config["modules"]
        self.killed = False

    def run(self, file: Path):
        """
        Performs processing logic.

        Parameters
        ----------
        file: Path
            The target file to process
        """
        self.process = mp.Process(target=self.apply_procedure, args=[file])
        self.process.start()
        logger.debug(f"Started processing with:\n{self.procedure.config}")

    def wait(self):
        """Waits for processing workflow to finish."""
        while self.process.is_alive():
            time.sleep(0.5)

    def apply_procedure(self, file: Path):
        """
        The processing logic to run in multiprocessing.

        Parameters
        ----------
        file: Path
            The target file to process
        """
        self.procedure.run(file)


class ProcessingScript(ProcessingConfig):
    """Processing workflow from scripts."""

    process: subprocess.Popen

    def __init__(self, path_to_config: Path | str):
        super().__init__(path_to_config)

    def update_config(self, path_to_config: Path | str):
        """
        Updates processing workflow information.

        Parameters
        ----------
        path_to_config: Path | str
            File path to processing workflow configuration
        """
        new_config = CONFIG_PATH.joinpath(path_to_config)
        self.procedure = [new_config]
        self.killed = False

    def run(self, file: Path):
        """
        Performs processing logic.

        Parameters
        ----------
        file: Path
            The target file to process
        """
        assert isinstance(self.procedure, list)
        if self.procedure[0].suffix == ".bat" and file.suffix == ".hex":
            file = file.with_suffix("")
        try:
            self.process = subprocess.Popen(
                self.procedure + [file],
                shell=False,
            )
        except subprocess.CalledProcessError as error:
            if error.stderr:
                logger.error(error.stderr)
            raise error
        except TypeError as error:
            logger.error(f"Wrong input type: {error}")

    def wait(self):
        """Waits for processing workflow to finish."""
        self.process.wait()
