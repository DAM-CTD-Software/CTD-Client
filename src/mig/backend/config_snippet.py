from ConfigParser import SafeConfigParser


section_names = 'official', 'debugging'


class MyConfiguration(object):

    def __init__(self, *file_names):
        parser = SafeConfigParser()
        parser.optionxform = str  # make option names case sensitive
        found = parser.read(file_names)
        if not found:
            raise ValueError('No config file found!')
        for name in section_names:
            # <-- here the magic happens
            self.__dict__.update(parser.items(name))


config = MyConfiguration('my.cfg', 'other.cfg')
