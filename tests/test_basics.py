from pathlib import Path
import unittest
from parameterized import parameterized
from ctdclient.bottles import BottleClosingDepths
from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.dshipcaller import DSHIPHeader
from ctdclient.batchprocessing import BatchProcessing
from ctdclient.runseasave import RunSeasave
import platform
import sys

if platform.system() == "Linux":
    config_path = "linux_config.toml"
elif platform.system() == "Windows":
    config_path = "ctdclient.toml"
else:
    sys.exit(1)


class TestConfig(unittest.TestCase):

    def setUp(self) -> None:
        self.config = ConfigurationFile(config_path)

    def test_basic_loading(self):
        self.assertEqual(len(self.config.data), 9)

    def test_basic_modify(self):
        self.config.modify("blub", "test")
        self.assertEqual(len(self.config.data), 10)
        self.config.modify(["number_of_bottles"], 5)
        self.assertEqual(self.config["number_of_bottles"], 5)

    def test_setitem(self):
        self.config["number_of_bottles"] = 15
        self.assertEqual(self.config["number_of_bottles"], 15)


class TestBottles(unittest.TestCase):

    def setUp(self):
        config = ConfigurationFile(config_path)
        self.bottles = BottleClosingDepths(config)

    def test_correct_base_dict(self):
        self.assertEqual(len(self.bottles), 13)
        self.assertEqual(list(self.bottles), [c for c in range(1, 14)])

    def test_bottle_instantiation(self):
        self.bottles.config.number_of_bottles = 17
        self.bottles.instantiate_bottle_info()
        self.assertEqual(self.bottles.number_of_bottles, 17)
        self.assertEqual(
            self.bottles.data,
            {number: "" for number in range(1, 18)},
        )


class TestMetadataHeader(unittest.TestCase):

    def setUp(self):
        self.config = ConfigurationFile(config_path)
        self.header = DSHIPHeader(self.config, dummy=True)
        self.expected_output = "Cruise = EMB295\nStation = EMB295_3-1\nPlatform = CTD\nCast = 0003\nOperator = Jan Donath\nGPS_Time = 04.07.2022 07:51:16\nPos_Alias = Gotland\nWsStartID = 76"

    def tearDown(self):
        self.header.end_listener()

    @parameterized.expand(
        [
            ("Station", "EMB295_3-1", "003-01"),
            ("GPS_Lat", "57 18.99193", "57 18.992 N"),
            ("GPS_Lon", "20  7.96432", "20  7.964 E"),
            ("Echo_Depth", "248.023438423", " 248.0 m"),
            ("Air_Pressure", "1014.523132", " 1014.5 hPa"),
            ("Pos_Alias", "Gotland", "Gotland"),
        ]
    )
    def test_value_formatter(self, name, value, result):
        self.assertEqual(
            self.header.format_dship_response(name, value), result
        )

    def test_full_header(self):
        self.header.dship_values = {
            "Cruise": "EMB295",
            "Station": "EMB295_3-1",
            "GPS_Time": "04.07.2022 07:51:16",
            "Pos_Alias": "Gotland",
        }
        self.assertEqual(
            self.header.build_metadata_header("CTD", "3", "Jan Donath"),
            self.expected_output,
        )


class TestSeasaveRun(unittest.TestCase):

    def setUp(self):
        self.config = ConfigurationFile(config_path)
        self.seasave = RunSeasave(self.config, "")

    def test_psa_set_run_infos(self):
        self.seasave.set_psa_run_info("unittest_seasave")
        psa_position = self.config.psa["SeasaveProgramSetup"]["Settings"]
        self.assertEqual(
            psa_position["ConfigurationFilePath"]["@value"], self.config.xmlcon
        )
        self.assertEqual(
            Path(psa_position["DataFilePath"]["@value"]),
            self.config.last_filename,
        )


class TestProcessing(unittest.TestCase):

    def setUp(self) -> None:
        self.config = ConfigurationFile(config_path)
        self.processing = BatchProcessing(
            self.config,
            {
                "DatCnv": "DatCnv1.psa",
                "WildEdit": "WildEdit1.psa",
                "W_Filter": "W_Filter1.psa",
                "BinAvg": "BinAvgK.psa",
            },
        )

    def test_class_finder(self):
        self.processing.get_processing_configs()
        self.assertEqual(len(self.processing.final_steps), 4)


class DSHIP(unittest.TestCase):

    def setUp(self) -> None:
        self.config = ConfigurationFile(config_path)
        self.dship = DSHIPHeader(self.config, dummy=True)

    def tearDown(self):
        self.dship.end_listener()

    def test_dummy(self):
        self.assertTrue(self.dship.alive)


class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.config = ConfigurationFile(config_path)
        # self.dship = DSHIPHeader(self.config, dummy=True)
        self.bottles = BottleClosingDepths(self.config)

    def test_simulate_start_seasave_in_view(self):
        self.bottles.update_bottle_information({1: -1, 2: 32, 3: "Bo"})
        self.config.psa.set_metadata_header(["test = bums", "test2 = bums2"])
        self.seasave = RunSeasave(
            self.config, "test.hex", "integration_test_seasave"
        )
        output = []
        with open("tests/data/integration_test_seasave.psa") as file:
            for line in file:
                output.append(line)
        expected_output = []
        with open("tests/data/expected_integration_test.psa") as file:
            for line in file:
                expected_output.append(line)
        # self.assertEqual(output, expected_output)
