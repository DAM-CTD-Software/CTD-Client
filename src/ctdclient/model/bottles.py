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

    def set_psa_bottle_info(self):
        """
        Calls the psa editing method of SeasavePsa of the seabirdfilehandler
        in order to generate the XML code necessary to set the bottle layout.
        """
        self.config.psa.set_bottle_fire_info(
            bottle_info=self.data, number_of_bottles=self.number_of_bottles
        )
