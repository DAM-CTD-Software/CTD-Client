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
        self.xml = config.psa
        self.instantiate_bottle_info()

    def instantiate_bottle_info(self):
        """Sets a default bottle layout according to the configuration file."""
        self.number_of_bottles = self.config["user"]["number_of_bottles"]
        self.data = {
            number + 1: '' for number in range(self.number_of_bottles)
        }
        for key, value in self.config["user"]["bottle_layout"].items():
            if int(key) in self.data.keys():
                self.data[int(key)] = value

    def update_bottle_information(self, info: dict, save_info=False):
        """
        Workhouse method that is being called from the outside to set a
        different bottle layout and to edit the psa.

        Parameters
        ----------
        info: dict : bottle layout information in the format specified above

        save_info: boolean : allows to write this bottle layout to the config
             (Default value = True)

        Returns
        -------

        """
        # assert len(self.data) == len(info)
        if isinstance(info, dict):
            self.data = info
        if save_info:
            self.write_new_config()
        self.update_psa()

    def write_new_config(self):
        """Writes the current bottle layout to the configuration file"""
        for key, value in self.data.items():
            self.config.modify(["user", "bottle_layout", str(key)], value)
        self.config.write()

    def update_psa(self):
        """
        Calls the psa editing method of SeasavePsa of the seabirdfilehandler
        in order to generate the XML code necessary to set the bottle layout.
        """
        self.xml.set_bottle_fire_info(self.data)
