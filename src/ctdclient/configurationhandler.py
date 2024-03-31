import tomlkit
from tomlkit.toml_file import TOMLFile
from seabirdfilehandler import SeasavePsa
from code_tools.logging import configure_logging, get_logger

configure_logging(f"{__name__}.log")
logger = get_logger(__name__)


class ConfigurationFile:
    """
    A python representation of the configuration file, linux_config.toml or
    windows_config.toml.
    The individual key value pairs can be targeted via basic dict-like chaining
    of keys, e.g.: config['user']['processing']['psas']
    """

    def __init__(self, path_to_config):
        self.path_to_config = path_to_config
        self.data = TOMLFile(path_to_config).read()
        # TODO: handle non-presence of the psa
        self.psa = SeasavePsa(self.data["user"]["paths"]["psa"])

    def __str__(self):
        return self.path_to_config

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, keys, value):
        self.modify([keys], value)

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
                    current_section = current_section.get(position, tomlkit.table())

                current_section[key[-1]] = value
            else:
                self.data.update({key: value})
        except ValueError as error:
            logger.error(f"Value modification failed: {error}")

    def reload(self):
        """Reopens the configuration file."""
        self.data = TOMLFile(self.path_to_config).read()
        self.psa = SeasavePsa(self.data["user"]["paths"]["psa"])
