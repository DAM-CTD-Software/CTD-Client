import pytest
from ctdclient.model.psa import SeasavePsa


@pytest.fixture
def psa() -> SeasavePsa:
    return SeasavePsa("Seasave.psa")


def test_comma2dot(psa):
    bottle_info = {1: "not,a,number", 2: "2,0", 3: "3.0", 4: "", 5: "-23.3"}
    psa.set_bottle_fire_info(
        bottle_info=bottle_info, number_of_bottles=len(bottle_info)
    )
    expected_bottle_values = {
        "1": "0.0",
        "2": "2.0",
        "3": "3.0",
        "4": "0.0",
        "5": "0.0",
    }
    for row in psa.settings_part["WaterSamplerConfiguration"]["AutoFireData"][
        "DataTable"
    ]["Row"]:
        if row["@BottleNumber"] in expected_bottle_values:
            assert (
                row["@FireAt"] == expected_bottle_values[row["@BottleNumber"]]
            )
