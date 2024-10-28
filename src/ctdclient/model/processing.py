import multiprocessing as mp
import subprocess
from pathlib import Path
from time import sleep

from code_tools.logging import get_logger
from processing.procedure import Procedure
from processing.settings import Configuration


logger = get_logger(__name__)


class Processing:

    current_config: Path
    procedure: Procedure | list
    process: mp.Process | subprocess.Popen

    def update_config(
        self,
        path_to_config: Path | str,
        procedure_fingerprint_directory: str,
        file_type_dir: str,
    ):
        new_config = Path(path_to_config)
        config_suffix = new_config.suffix
        if config_suffix == ".toml":
            config = Configuration(new_config)
            if len(procedure_fingerprint_directory) == 0:
                procedure_fingerprint_directory = None
            self.procedure = Procedure(
                config,
                auto_run=False,
                procedure_fingerprint_directory=procedure_fingerprint_directory,
                file_type_dir=file_type_dir,
            )
        else:
            self.procedure = [new_config]
        self.current_config = new_config

    def run(self, file: Path | str):
        if isinstance(self.procedure, Procedure):
            self.process = mp.Process(
                target=self.procedure.run, args=[Path(file)]
            )
            self.process.start()
            while self.process.is_alive():
                sleep(0.1)
        else:
            self._run_custom_script(Path(file))
        logger.info(f"Ran processing of file {str(Path(file).name)}")

    def _run_custom_script(self, file: Path):
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

    def cancel(self):
        self.process.kill()
