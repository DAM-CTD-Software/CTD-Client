from __future__ import annotations

import logging
import multiprocessing as mp
import subprocess
from abc import ABC
from abc import abstractmethod
from collections import UserList
from pathlib import Path

from ctdclient.definitions import config
from ctdclient.definitions import event_manager
from ctdclient.definitions import TEMPLATE_PATH
from processing.procedure import Procedure
from processing.settings import Configuration

logger = logging.getLogger(__name__)


class ProcessingList(UserList):
    data: list[ProcessingConfig]

    def read_processing_files(self):
        # reset processing configs
        self.data = []
        for file in config.processing_dir.glob("*proc*"):
            try:
                self.data.append(self.create_new_processing_config(file))
            except Exception:
                continue

    def run(self, file: Path | str):
        for proc_config in self.data:
            if proc_config.active:
                proc_config.run(Path(file))

    def cancel(self):
        for proc_config in self.data:
            if proc_config.active:
                proc_config.cancel()

    def toggle_config_activity_state(self, proc_config: ProcessingConfig):
        for proc in self.data:
            if proc == proc_config:
                proc.active = not proc.active
                return True
        logger.error(
            f"Could not set active processing: {proc_config.path_to_config}"
        )
        return False

    def create_new_processing_config(self, file: Path) -> ProcessingConfig:
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
        if not template_path.exists():
            return None
        template = self.create_new_processing_config(template_path)
        self.data.append(template)
        return template

    def remove_config(self, config: ProcessingConfig):
        self.data.remove(config)
        if config.path_to_config.exists():
            config.path_to_config.unlink()


class ProcessingConfig(ABC):
    current_config: Path
    process: mp.Process | subprocess.Popen

    def __init__(
        self,
        path_to_config: Path | str,
    ):
        self.update_config(path_to_config)
        self.path_to_config = Path(path_to_config)
        self.name = self.path_to_config.name
        self.active = (
            True if self.name == config.last_processing_file.name else False
        )

    def __str__(self) -> str:
        return str(self.path_to_config)

    def __repr__(self) -> str:
        return self.__str__()

    @abstractmethod
    def run(self, file: Path):
        pass

    @abstractmethod
    def update_config(self, path_to_config: Path | str):
        pass

    def post_processing_clean_up(self, file):
        if not self.killed:
            config.last_processing_file = self.path_to_config.absolute()
            config.write()
            event_manager.publish(
                "processing_successful", target=Path(file).absolute()
            )

    def cancel(self):
        self.process.kill()
        self.killed = True


class ProcessingProcedure(ProcessingConfig):
    def __init__(self, path_to_config: Path | str):
        super().__init__(path_to_config)

    def update_config(
        self,
        path_to_config: Path | str,
        procedure_fingerprint_directory: str | None = None,
        file_type_dir: str = "",
    ):
        new_config = Path(path_to_config)
        proc_config = Configuration(new_config)
        self.procedure = Procedure(
            proc_config,
            seabird_exe_directory=config.path_to_proc_exes,
            auto_run=False,
            procedure_fingerprint_directory=procedure_fingerprint_directory,
            file_type_dir=file_type_dir,
        )
        self.modules = proc_config["modules"]
        self.killed = False

    def run(self, file: Path):
        self.process = mp.Process(target=self.apply_procedure, args=[file])
        self.process.start()
        logger.debug(f"Started processing with:\n{self.procedure.config}")

    def apply_procedure(self, file: Path):
        self.procedure.run(file)
        self.post_processing_clean_up(file)


class ProcessingScript(ProcessingConfig):
    def __init__(self, path_to_config: Path | str):
        super().__init__(path_to_config)

    def update_config(self, path_to_config: Path | str):
        new_config = Path(path_to_config)
        self.procedure = [new_config]
        self.killed = False

    def run(self, file: Path):
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
        else:
            self.process.wait()
            self.post_processing_clean_up(file)
