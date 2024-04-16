from pathlib import Path
import tomlkit
from tomlkit.toml_file import TOMLFile
from seabirdfilehandler import SeasavePsa
from code_tools.logging import configure_logging, get_logger

configure_logging(f"{__name__}.log")
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
        self.psa = SeasavePsa(self.data["user"]["paths"]["seasave_psa"])
        self.read_config()

    def __str__(self):
        return str(self.path_to_config)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, keys, value):
        self.modify([keys], value)

    def read_config(self):
        self.data = TOMLFile(self.path_to_config).read()
        self.platforms: list = self.data["platforms"]
        assert isinstance(self.platforms, list)
        self.number_of_bottles: int = self.data["number_of_bottles"]
        self.path_to_seasave: Path = Path(self.data["paths"]["seasave_exe"])
        self.path_to_processing_exes: Path = Path(
            self.data["paths"]["processing_exes"]
        )
        self.dship_ip: str = self.data["dship"]["ip"]
        self.dhsip_fetch_intervall: float = float(
            self.data["dship"]["fetch_intervall"]
        )
        self.dship_api_target_names: dict = self.data["dship"]["identifier"]
        assert isinstance(self.dship_api_target_names, dict)
        self.last_cast: int = self.data["history"]["last_cast"]
        self.last_filename: Path = Path(self.data["history"]["last_filename"])
        self.last_platform: str = self.data["history"]["last_platform"]
        self.read_user_config()

    def read_user_config(self):
        self.output_directory: Path = Path(
            self.data["user"]["paths"]["output_directory"]
        )
        self.xmlcon: Path = Path(self.data["user"]["paths"]["xmlcon"])
        self.seasave_psa: Path = Path(
            self.data["user"]["paths"]["seasave_psa"]
        )
        self.processing_type: str = self.data["user"]["processing"][
            "type"
        ].lower()
        self.path_to_batch: Path = Path(
            self.data["user"]["processing"]["batch_path"]
        )
        self.psa_directory: Path = Path(
            self.data["user"]["processing"]["psa_directory"]
        )
        self.processing_modules: list = self.data["user"]["processing"][
            "modules"
        ]
        assert isinstance(self.processing_modules, list)
        self.operators: dict = self.data["user"]["operators"]
        assert isinstance(self.operators, dict)

    def set_config(self):
        self.data["history"]["last_cast"] = self.last_cast
        self.data["history"]["last_filename"] = str(self.last_filename)
        self.data["history"]["last_platform"] = self.last_platform
        self.data["user"]["paths"]["output_directory"] = str(
            self.output_directory
        )
        self.data["user"]["paths"]["xmlcon"] = str(self.xmlcon)
        self.data["user"]["paths"]["seasave_psa"] = str(self.seasave_psa)
        self.data["user"]["processing"]["type"] = self.processing_type
        self.data["user"]["processing"]["batch_path"] = str(self.path_to_batch)
        self.data["user"]["processing"]["psa_directory"] = str(
            self.psa_directory
        )
        self.data["user"]["processing"]["modules"] = self.processing_modules
        self.data["user"]["operators"] = self.operators

    def write(self, path_to_write=None):
        """
        Writes changes to the configuration file to the disk.

        Parameters
        ----------
        path_to_write :
             (Default value = None)

        Returns
        -------

        """
        self.set_config()
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
        else:
            logger.info(f"Wrote new configuration {output_path} to disk.")

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
