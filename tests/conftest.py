from pathlib import Path

import pytest
from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.eventmanager import EventManager
from ctdclient.model.processing import Processing
from processing.procedure import Procedure

data_dir = Path("seabird_example_data/cnv")
target_file = data_dir.joinpath("basic_emb.cnv")
output_name = "basic_emb_4coriolis.cnv"


def _help(*args, **kwargs):
    assert True


@pytest.fixture
def processing() -> Processing:
    config = ConfigurationFile("templates/ctdclient.toml")
    event_manager = EventManager()
    event_manager.subscribe("processing_successful", _help)
    return Processing(config, event_manager)


@pytest.fixture
def simple_processing(processing: Processing) -> Processing:
    # very easy, one step processing that outputs a standard file name
    processing.procedure = Procedure(
        configuration={
            "input": [target_file],
            "output_type": "cnv",
            "output_name": output_name,
            "modules": {
                "abs_sal": {},
            },
        },
        auto_run=False,
    )
    processing.current_config = Path("templates/processing_template.toml")
    processing.killed = False
    return processing


@pytest.fixture
def empty_processing(processing: Processing) -> Processing:
    # serves only as trigger for nrt pubs
    processing.procedure = Procedure(
        configuration={
            "input": [target_file],
            "output_type": "cnv",
            "modules": {},
        },
        auto_run=False,
    )
    return processing


@pytest.fixture
def fresh_target_file() -> Path:
    file_name = "test_4coriolis.cnv"
    fresh_file = data_dir.joinpath(file_name)
    fresh_file.touch()
    return fresh_file
