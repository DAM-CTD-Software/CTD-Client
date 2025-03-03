from __future__ import annotations

import multiprocessing as mp
import subprocess
from collections import UserList
from pathlib import Path
from time import sleep

from code_tools.logging import get_logger
from ctdclient.definitions import config
from ctdclient.definitions import event_manager
from ctdclient.definitions import TEMPLATE_PATH
from processing.procedure import Procedure
from processing.settings import Configuration

logger = get_logger(__name__)


class ProcessingList(UserList):
    def __init__(self):
        pass

    def read_processing_files(self):
        # reset processing configs
        self.data = []
        for file in config.processing_dir.glob("*proc*"):
            try:
                self.data.append(self.create_new_processing_config(file))
            except Exception as error:
                continue
        self.set_active_config()

    def set_active_config(self, proc_config: ProcessingConfig | None = None):
        processing = (
            proc_config.path_to_config
            if proc_config
            else config.last_processing_file
        )
        for proc in self.data:
            if proc.path_to_config.absolute() == processing:
                proc.active = True
                return True
        logger.error(f"Could not set active processing: {processing}")
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


class ProcessingConfig:
    current_config: Path
    process: mp.Process | subprocess.Popen

    def __init__(
        self,
        path_to_config: Path | str,
    ):
        self.update_config(path_to_config)
        self.path_to_config = Path(path_to_config)
        self.name = self.path_to_config.name
        self.active = False

    def update_config(self, path_to_config: Path | str):
        pass

    def post_processing_clean_up(self, file):
        if not self.killed:
            config.last_processing_file = self.current_config
            config.write()
            event_manager.publish(
                "processing_successful", target=Path(file).absolute()
            )
            logger.info(f"Processed {file} using {self.current_config}")

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
        config = Configuration(new_config)
        self.procedure = Procedure(
            config,
            auto_run=False,
            procedure_fingerprint_directory=procedure_fingerprint_directory,
            file_type_dir=file_type_dir,
        )
        self.current_config = new_config
        self.killed = False

    def run(self, file: Path | str):
        self.process = mp.Process(target=self.procedure.run, args=[Path(file)])
        self.process.start()
        while self.process.is_alive():
            sleep(0.1)
        self.post_processing_clean_up(file)


class ProcessingScript(ProcessingConfig):
    def __init__(self, path_to_config: Path | str):
        super().__init__(path_to_config)

    def update_config(self, path_to_config: Path | str):
        new_config = Path(path_to_config)
        self.procedure = [new_config]
        self.current_config = new_config
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
