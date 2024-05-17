from pathlib import Path
import tomlkit
from tomlkit.toml_file import TOMLFile
from tomlkit.exceptions import NonExistentKey, KeyAlreadyPresent, EmptyKeyError
import sys
from seabirdfilehandler import SeasavePsa
from code_tools.logging import get_logger

logger = get_logger(__name__)


class ConfigurationFile:
    """
    A python representation of the configuration file, ctdclient.toml .
    The individual key value pairs can be targeted via basic dict-like chaining
    of keys, e.g.: config['user']['processing']['psas']
    """

    def __init__(self, path_to_config: Path | str):
        self.path_to_config = Path(path_to_config)
        self.data = TOMLFile(self.path_to_config).read()
        self.read_config()

    def __str__(self):
        return str(self.path_to_config)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, keys, value):
        self.modify([keys], value)

    def read_config(self, ctd_type=None):
        self.data = TOMLFile(self.path_to_config).read()
        try:
            self.platforms: list = self.data["platforms"]
            assert isinstance(self.platforms, list)
            self.last_platform: str = self.data["last_platform"]
            assert isinstance(self.last_platform, str)
            self.path_to_seasave: Path = Path(self.data["seasave_exe"])
            self.path_to_processing_exes: Path = Path(
                self.data["processing_exes"]
            )
            self.number_of_bottles: int = self.data["number_of_bottles"]
            assert isinstance(self.number_of_bottles, int)
            self.dship_ip: str = self.data["dship"]["ip"]
            self.dhsip_fetch_intervall: float = float(
                self.data["dship"]["fetch_intervall"]
            )
            self.dship_api_target_names: dict = self.data["dship"][
                "identifier"
            ]
            assert isinstance(self.dship_api_target_names, dict)
            self.operators: dict = self.data["operators"]
            assert isinstance(self.operators, dict)
            if not ctd_type:
                ctd_type = self.last_platform.lower()
            self.read_ctd_config(ctd_type)
        except (NonExistentKey, EmptyKeyError, KeyAlreadyPresent) as error:
            logger.error(f"Invalid configuration file: {error}")
            sys.exit(1)

    def read_ctd_config(self, ctd_type: str):
        try:
            self.ctd_info: dict = self.data[ctd_type]
            self.psa = SeasavePsa(self.data[ctd_type]["paths"]["seasave_psa"])
            assert isinstance(self.ctd_info, dict)
            self.seasave_psa: Path = Path(
                self.data[ctd_type]["paths"]["seasave_psa"]
            )
            self.output_directory: Path = Path(
                self.data[ctd_type]["paths"]["output_directory"]
            )
            self.xmlcon: Path = Path(self.data[ctd_type]["paths"]["xmlcon"])
            self.path_to_batch: Path = Path(
                self.data[ctd_type]["paths"]["batch_path"]
            )
            self.psa_directory: Path = Path(
                self.data[ctd_type]["paths"]["psa_directory"]
            )
            self.last_cast: int = self.data[ctd_type]["memory"]["last_cast"]
            self.last_filename: Path = Path(
                self.data[ctd_type]["memory"]["last_filename"]
            )
            self.last_processing_file: Path = Path(
                self.data[ctd_type]["memory"]["last_processing_file"]
            )
        except (NonExistentKey, EmptyKeyError, KeyAlreadyPresent) as error:
            logger.error(f"Mistake in update: {error}")
            sys.exit(1)

    def set_config(self, ctd_type: str):
        self.data["last_platform"] = self.last_platform
        self.data["operators"] = self.operators
        self.data[ctd_type]["paths"]["seasave_psa"] = str(self.seasave_psa)
        self.data[ctd_type]["paths"]["output_directory"] = str(
            self.output_directory
        )
        self.data[ctd_type]["paths"]["xmlcon"] = str(self.xmlcon)
        self.data[ctd_type]["paths"]["batch_path"] = str(self.path_to_batch)
        self.data[ctd_type]["paths"]["psa_directory"] = str(self.psa_directory)
        self.data[ctd_type]["memory"]["last_cast"] = self.last_cast
        self.data[ctd_type]["memory"]["last_filename"] = str(
            self.last_filename
        )
        self.data[ctd_type]["memory"]["last_processing_file"] = str(
            self.last_processing_file
        )

    def write(
        self,
        current_platform=None,
        use_internal_values=True,
        path_to_write=None,
    ):
        """
        Writes changes to the configuration file to the disk.

        Parameters
        ----------
        path_to_write :
             (Default value = None)

        Returns
        -------

        """
        if use_internal_values:
            current_platform = (
                self.last_platform.lower()
                if current_platform is None
                else current_platform.lower()
            )
            self.set_config(current_platform)
        output_path = self.path_to_config
        if path_to_write:
            output_path = path_to_write
        out_str = tomlkit.dumps(self.data)
        out_str = out_str.replace("\r", "")
        try:
            with open(output_path, "w") as file:
                file.write(out_str)
        except IOError as error:
            logger.error(f"Could not write configuration file: {error}")

    def modify(self, key, value):
        """
        Modifies the configuration values inside of this python representation.
        Does not write anything to disk.

        Parameters
        ----------
        key :

        value :


        Returns
        -------

        """
        try:
            if isinstance(key, list):
                current_section = self.data
                for position in key[:-1]:
                    current_section = current_section.get(
                        position, tomlkit.table()
                    )

                current_section[key[-1]] = value
            else:
                self.data.update({key: value})
        except ValueError as error:
            logger.error(f"Value modification failed: {error}")

    def reload(self):
        """Reopens the configuration file."""
        self.read_config()
