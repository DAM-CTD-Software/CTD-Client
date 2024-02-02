import unittest
from ctdclient.bottles import BottleClosingDepths
from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.dshipcaller import DSHIPHeader
from ctdclient.processing import BatchProcessing
from ctdclient.runseasave import RunSeasave
import platform
import sys

if platform.system() == 'Linux':
    config_path = 'linux_config.toml'
elif platform.system() == 'Windows':
    config_path = 'windows_config.toml'
else:
    sys.exit(1)


class TestConfig(unittest.TestCase):

    def setUp(self) -> None:
        self.config = ConfigurationFile(config_path)

    def test_basic_loading(self):
        self.assertEqual(len(self.config.data), 5)

    def test_basic_modify(self):
        self.config.modify('blub', 'test')
        self.assertEqual(len(self.config.data), 6)
        self.config.modify(['user', 'number_of_bottles'], 5)
        self.assertEqual(self.config['user']['number_of_bottles'], 5)
        self.config.modify(['user', 'bottle_layout'], {'1': 2, '2': 1})
        self.assertEqual(len(self.config['user']['bottle_layout']), 2)
        self.config.modify(['user', 'new'], 'lol')
        self.assertEqual(len(self.config['user']['new']), 3)
        # self.config.write()

    def test_setitem(self):
        self.config['user']['number_of_bottles'] = 15
        self.assertEqual(self.config['user']['number_of_bottles'], 15)


class TestBottles(unittest.TestCase):

    def setUp(self):
        config = ConfigurationFile(config_path)
        self.bottles = BottleClosingDepths(config)

    def test_correct_base_dict(self):
        self.assertEqual(len(self.bottles), 13)
        self.assertEqual(list(self.bottles), [c for c in range(1, 14)])

    def test_xmlcon_entry(self):
        length_before = len(self.bottles.xml)
        bottle_dict = {key: key for key in range(1, 14)}
        self.bottles.update_bottle_information(bottle_dict)
        self.assertEqual(len(self.bottles.xml), length_before)

    def test_bottle_instantiation(self):
        self.bottles.config['user']['number_of_bottles'] = 17
        self.bottles.instantiate_bottle_info()
        self.assertEqual(self.bottles.number_of_bottles, 17)
        self.assertEqual(self.bottles.data, {
                         number: 0.0 if number > 13 else number
                         for number in range(1, 18)})


class TestMetadataHeader(unittest.TestCase):

    def setUp(self):
        self.config = ConfigurationFile(config_path)
        self.header = DSHIPHeader(self.config, dummy=True)

    def tearDown(self):
        self.header.end_listener()

    def test_xml_header_format(self):
        pass


class TestSeasaveRun(unittest.TestCase):

    def setUp(self):
        self.config = ConfigurationFile(config_path)
        self.seasave = RunSeasave(self.config)

    def test_psa_set_run_infos(self):
        self.seasave.set_psa_run_info()
        psa_position = self.config.psa['SeasaveProgramSetup']['Settings']
        self.assertEqual(psa_position['ConfigurationFilePath']['@value'],
                         self.config['user']['paths']['xmlcon'])
        self.assertEqual(psa_position['DataFilePath']['@value'],
                         self.config['user']['paths']['hex'])


class TestProcessing(unittest.TestCase):

    def setUp(self) -> None:
        self.config = ConfigurationFile(config_path)
        self.processing = BatchProcessing(
            self.config, {'DatCnv': 'DatCnv1.psa',
                          'WildEdit': 'WildEdit1.psa',
                          'W_Filter': 'W_Filter1.psa',
                          'BinAvg': 'BinAvgK.psa'})

    def test_class_finder(self):
        self.processing.get_processing_configs()
        self.assertEqual(len(self.processing.final_steps), 4)

    def test_run(self):
        # self.processing.run()
        self.assertTrue


class DSHIP(unittest.TestCase):

    def setUp(self) -> None:
        self.config = ConfigurationFile(config_path)
        self.dship = DSHIPHeader(self.config, dummy=True)

    def tearDown(self):
        self.dship.end_listener()

    def test_dummy(self):
        self.assertTrue(self.dship.alive)
