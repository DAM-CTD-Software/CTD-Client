from tomlkit import dumps, table
from tomlkit.toml_file import TOMLFile
from seabirdfilehandler import SeasavePsa


class ConfigurationFile:

    def __init__(self, path_to_config):
        self.path_to_config = path_to_config
        self.data = TOMLFile(path_to_config).read()
        self.psa = SeasavePsa(self.data['user']['paths']['psa'])
        # except (FileNotFoundError, ValueError) as error:
        #     print(f'Could not load configuration file: {error}')
        # else:
        #     pass

    def __str__(self):
        return self.path_to_config

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, keys, value):
        self.modify([keys], value)

    def write(self, path_to_write=None):
        output_path = self.path_to_config
        if path_to_write:
            output_path = path_to_write
        try:
            with open(output_path, 'w') as file:
                file.write(dumps(self.data))
        except IOError as error:
            print(f'Could not write configuration file: {error}')

    def modify(self, key, value):
        try:
            if isinstance(key, list):
                current_section = self.data
                for position in key[:-1]:
                    current_section = current_section.get(position, table())

                current_section[key[-1]] = value
            else:
                self.data.update({key: value})
        except ValueError as error:
            print(f'Value modification failed: {error}')

    def reload(self):
        self.data = TOMLFile(self.path_to_config).read()
        self.psa = SeasavePsa(self.data['user']['paths']['psa'])
