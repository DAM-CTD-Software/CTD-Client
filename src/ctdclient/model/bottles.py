from collections import UserDict


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
        new_data_table = {}
        for key, value in bottle_data_table.items():
            if key in new_data_table:
                continue
            if value in list(new_data_table.values()):
                other_key = list(new_data_table.keys())[
                    list(new_data_table.values()).index(value)
                ]
                new_data_table[other_key] = str(
                    int(value) - (self.config.minimum_bottle_diff / 2)
                )
                value = str(int(value) + (self.config.minimum_bottle_diff / 2))
            new_data_table[key] = value
        self.data = new_data_table
