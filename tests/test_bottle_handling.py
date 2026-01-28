import logging

from conftest import example_data
import pytest
from ctdclient.model.bottles import BottleClosingDepths
from ctdclient.model.psa import SeasavePsa

logger = logging.getLogger(__name__)
logger.propagate = True

@pytest.fixture
def psa() -> SeasavePsa:
    return SeasavePsa(example_data.joinpath("psa","Seasave.psa"))


def test_comma2dot(psa):
    bottle_info = {
        1: "not,a,number",
        2: "2,0",
        3: "3.0",
        4: "",
        5: "-23.3",
        6: "H2S",
        7: "456.7",
    }
    psa.set_bottle_fire_info(
        bottle_info=bottle_info, number_of_bottles=len(bottle_info)
    )
    expected_bottle_values = {
        "1": "0.0",
        "2": "2.0",
        "3": "3.0",
        "4": "0.0",
        "5": "0.0",
        "6": "0.0",
        "7": "456.7",
    }
    for row in psa.settings_part["WaterSamplerConfiguration"]["AutoFireData"][
        "DataTable"
    ]["Row"]:
        if row["@BottleNumber"] in expected_bottle_values:
            assert row["@FireAt"] == expected_bottle_values[row["@BottleNumber"]]


@pytest.mark.parametrize(
    "test_data", [[{1: '2', 2: '5', 3: '8', 4: '19'}, {1: '2.0', 2: '5.0', 3: '8.0', 4: '19.0'}],
                  [{1: '2', 2: 'test', 3: '1.2', 4: '1,6'}, {1: '2.0' , 3: '1.2', 4: '1.6'}],
                  [{5: '5', 3: '5'}, {5: '4.8', 3: '5.2'}],
                  [{5: '5,0', 3: '5'}, {5: '4.8', 3: '5.2'}],
                  [{10: 'two', 11: 'two'}, {}],
    ]
)
def test_same_depth_mapping(test_data, config):
    config.minimum_bottle_diff = 0.4
    config.number_of_bottles = len(test_data[0])
    bottles = BottleClosingDepths(config)
    bottles.check_bottle_data(test_data[0])
    for k, v in test_data[1].items():
        assert v == bottles[k]


def test_more_than_two_same_depth_mappings(config, caplog):
    caplog.set_level(logging.WARNING)
    test_data = {1: '1', 2: '1', 3: '1'}
    config.minimum_bottle_diff = 0.4
    config.number_of_bottles = len(test_data)
    bottles = BottleClosingDepths(config)
    bottles.check_bottle_data(test_data)
    assert 'Cannot close more than two bottles at the same depth automatically. Make sure to set the bottles to different depths or try to put your target bottles on the same release hook.' in caplog.text
