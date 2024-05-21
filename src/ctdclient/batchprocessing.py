from pathlib import Path
import subprocess
from code_tools.logging import get_logger
from processing import IncompleteConfigFile, ProcessingRoutine, Configuration
from tomlkit.exceptions import NonExistentKey

logger = get_logger(__name__)

# TODO: rename file


class MyProcessing:
    """"""

    def __init__(
        self,
        processing_info: dict | None = None,
        processing_config: Path | str | None = None,
        template: Path | str = Path("templates/processing_template.toml"),
    ):
        self.template = Configuration(template)
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
                logger.warning(
                    "Processing information is needed to run processing. Defaulting to template."
                )
        self.modules = self.processing_info["modules"]
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
        ProcessingRoutine(self.processing_info).run()
        self.save({"file_path": self.file_path, **self.processing_info})

    def save(self, info_dict: dict):
        new_file_path = info_dict["file_path"]
        del info_dict["file_path"]
        try:
            # check config file values
            ProcessingRoutine(info_dict)
        except IncompleteConfigFile:
            pass
        finally:
            new_file = Configuration(path=self.file_path)
            new_file.data = info_dict
            new_file.write(new_file_path)

    def load(self, path_to_file: Path | str) -> bool:
        config_file = Configuration(path_to_file)
        try:
            ProcessingRoutine(config_file.data)
        except IncompleteConfigFile as error:
            pass
        finally:
            self.config_file = config_file
            self.processing_info = config_file.data
            self.file_path = Path(path_to_file)
            self.modules = self.processing_info["modules"]
            return True


class WindowsBatch:
    """Simple class to only run the old windows batch we actually want to
    replace"""

    def __init__(self, batch: Path | str, hex_file: Path | str):
        try:
            self.batch = Path(batch)
            hex_file = Path(hex_file)
            self.hex_file = hex_file.parent.joinpath(hex_file.stem)
        except TypeError as error:
            logger.error(f"Wrong input type: {error}")
        else:
            self.run(self.hex_file)

    def run(self, hex_file):
        try:
            ps = subprocess.Popen([self.batch, hex_file], shell=False)
            if ps.stdout:
                logger.debug(ps.stdout)
        except subprocess.CalledProcessError as error:
            if error.stderr:
                logger.error(error.stderr)
            raise error
        else:
            logger.info(f"Ran processing: {self.batch} {hex_file}")
