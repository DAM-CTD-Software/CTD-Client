from pathlib import Path
import json
import pytest
from ctdclient.model.dshipcaller import get_ctd_last_event
from ctdclient.model.dshipcaller import get_station_id
from ctdclient.model.fileupdater import UpdateFiles
from seabirdfilehandler.seabirdfiles import SeaBirdFile

station_event_info = "MSM129/1_6-1"
test_file = "MSM129_1_000-00_CTD_0022.hex"
test_dir = Path("tests/data")
with open("manida_export.json", "r") as file:
    json_info = file.read()


@pytest.fixture
def update() -> UpdateFiles:
    return UpdateFiles(
        test_dir.joinpath(test_file),
        test_dir,
        station_event_info,
    )


def test_find_last_ctd_event():
    output = get_ctd_last_event(json_info)
    assert output["Device Shortname"].lower() == "ctd"
    assert output["Device Operation"] == "MSM129/1_7-1"


def test_correct_station_id():
    output = get_station_id(json.loads(json_info)["list"][0])
    assert output == "MSM129_1_0_Underway-1"


def test_metaheader_updater(update):
    update.replace_metadata_header_info(station_event_info)
    assert SeaBirdFile(test_dir.joinpath(test_file)).metadata[
        "Station"
    ] == station_event_info.replace("/", "_")


def test_new_file_name(update):
    output = update.create_new_file_name(test_file[:-4], station_event_info)
    assert output == "MSM129_1_006-01_CTD_0022"
