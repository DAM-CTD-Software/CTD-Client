import subprocess
from pathlib import Path
from time import sleep

from ctdclient.definitions import PROCESSING_TEMPLATE_PATH
from code_tools.logging import get_logger
from processing import Configuration
from processing import ProcessingRoutine
from tomlkit.exceptions import NonExistentKey

logger = get_logger(__name__)


class Processing:
    """"""

    def __init__(
        self,
        processing_info: dict | None = None,
        processing_config: Path | str | None = None,
        template: Path | str = PROCESSING_TEMPLATE_PATH,
    ):
        self.template = Configuration(template)
        self.optional_options = self.template["optional"]
        if processing_info:
            self.processing_info = processing_info
            # TODO: think about good default path here
            self.file_path = Path("")
        else:
            if processing_config:
                self.config_file = Configuration(Path(processing_config))
                self.processing_info = self.config_file.data
                self.file_path = self.config_file.path
            else:
                self.config_file = self.template
                self.processing_info = self.config_file.data
                self.file_path = self.config_file.path
        self.modules = self.processing_info["modules"]
        # TODO: extend these or handle differently
        self.psa_paths = [
            path.name
            for path in Path(self.processing_info["psa_directory"]).iterdir()
        ]
        self.psa_paths = sorted(self.psa_paths, key=str.lower)
        self.step_names = [
            "alignctd",
            "airpressure",
            "binavg",
            "bottlesum",
            "celltm",
            "datcnv",
            "derive",
            "filter",
            "iow_btl_id",
            "loopedit",
            "wildedit",
            "w_filter",
        ]
        self.input_file: Path | str

    def run(self):
        """Runs a processing routine according to the preset values."""
        # cheap hack to allow 'file_list' at specific position
        pre_files = {}
        for keys in ["exe_directory", "psa_directory"]:
            try:
                pre_files[keys] = self.processing_info.pop(keys)
            except NonExistentKey:
                pass
        for keys in ["file_path", "file_list"]:
            try:
                del self.processing_info[keys]
            except KeyError:
                pass
        self.processing_info = {
            **pre_files,
            "file_list": [self.input_file],
            **self.processing_info,
        }
        self.process = ProcessingRoutine(self.processing_info)
        self.process.start_thread()
        while self.process.run_thread.is_alive():
            sleep(1)
        self.save(self.processing_info)

    def cancel(self):
        try:
            self.process.cancel()
        except ValueError:
            pass

    def save(self, info_dict: dict):
        new_file = self.config_file
        new_file.data = info_dict
        new_file.write(self.file_path)

    def load(self, path_to_file: Path | str) -> bool:
        config_file = Configuration(path_to_file)
        self.config_file = config_file
        self.processing_info = config_file.data
        self.file_path = Path(path_to_file)
        self.modules = self.processing_info["modules"]
        return True


class WindowsBatch:
    """Simple class to only run the old windows batch we actually want to
    replace"""

    def __init__(self):
        pass

    def run(self, batch: Path | str, hex_file: Path | str):
        try:
            hex_file = Path(hex_file).parent.joinpath(Path(hex_file).stem)
            self.killed = False
            self.ps = subprocess.Popen(
                [batch, hex_file], shell=False
            )
            if self.ps.stdout:
                logger.debug(self.ps.stdout)
        except subprocess.CalledProcessError as error:
            if error.stderr:
                logger.error(error.stderr)
            raise error
        except TypeError as error:
            logger.error(f"Wrong input type: {error}")
        else:
            self.ps.wait()
            if self.killed:
                logger.info(f"Interupted processing: {batch}")
            else:
                logger.info(f"Ran processing: {batch} {hex_file}")

    def cancel(self):
        self.killed = True
        self.ps.kill()
