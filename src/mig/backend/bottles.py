from collections import UserDict


class BottleClosingTimes(UserDict):

    def __init__(self, config) -> None:
        self.config = config
        self.xml = config.psa
        self.instantiate_bottle_info()

    def instantiate_bottle_info(self):
        self.number_of_bottles = self.config['user']['number_of_bottles']
        self.data = {number+1: 0.0 for number in range(self.number_of_bottles)}
        for key, value in self.config['user']['bottle_layout'].items():
            if int(key) in self.data.keys():
                self.data[int(key)] = value

    def update_bottle_information(self, info: dict, save_info=True):
        # assert len(self.data) == len(info)
        if isinstance(info, dict):
            self.data = info
        if save_info:
            self.write_new_config()
        self.update_psa()

    def write_new_config(self):
        for key, value in self.data.items():
            self.config.modify(['user', 'bottle_layout', str(key)], value)
        self.config.write()

    def update_psa(self):
        self.xml.set_bottle_fire_info(self.data)
