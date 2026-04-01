import logging
from collections import Counter, UserDict

logger = logging.getLogger(__name__)


class BottleClosingDepths(UserDict):
    """
    Writes the pressure values one wants to close the bottles to the
    Seasave.psa in the required format. The class is instantiated with a
    default bottle layout which is set in the configuration file. To apply
    a closing setup, update_bottle_information() must be called with a dict
    of the following format:

            {BottleID: pressure value as difference from the air pressure,
                [str]: [str],
                    1: 4,
                    2: 6,
                    6: Bo}

    Parameters
    ----------
    config: ConfigurationFile

    """

    def __init__(self, config) -> None:
        self.config = config
        self.instantiate_bottle_info()

    def instantiate_bottle_info(self):
        """Sets a default bottle layout according to the configuration file."""
        self.number_of_bottles = self.config.number_of_bottles
        self.data = {
            number + 1: "" for number in range(self.number_of_bottles)
        }

    def check_bottle_data(self, bottle_data_table: dict):
        """
        Assures that are a maximum of two bottles are closed at the same depth.

        Sea-Birds water carousel is physically to slow to support the
        guaranteed closing of more bottles. To enable the input of more
        bottles on the same depth, they get shifted by a user-definable
        constant time.

        Parameters
        ----------
        bottle_data_table: dict
            The bottle data information

        """
        bottle_data_table = {
            k: str(float(v.replace(",", ".")))
            for k, v in bottle_data_table.items()
            if v.replace(",", ".").replace(".", "", 1).isdigit()
        }
        depth_counts = Counter(bottle_data_table.values())
        if [count for count in depth_counts.values() if count > 2]:
            logger.error(
                "Cannot close more than two bottles at the same depth automatically. Make sure to set the bottles to different depths or try to put your target bottles on the same release hook."
            )
            self.data = {1: "ERROR"}
            return
        new_data_table = {}
        for key, value in bottle_data_table.items():
            if key in new_data_table:
                continue
            if value in list(new_data_table.values()):
                other_key = list(new_data_table.keys())[
                    list(new_data_table.values()).index(value)
                ]
                new_data_table[other_key] = str(
                    float(value) - (self.config.minimum_bottle_diff / 2)
                )
                value = str(
                    float(value) + (self.config.minimum_bottle_diff / 2)
                )
            try:
                value = str(float(value))
            except ValueError:
                pass
            new_data_table[key] = value
        for n in range(1, self.number_of_bottles + 1):
            if n not in new_data_table:
                new_data_table[n] = ""
        self.data = {k: v for k, v in sorted(new_data_table.items())}
