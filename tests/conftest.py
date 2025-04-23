import datetime
from pathlib import Path

import pytest
from ctdclient.model.processing import ProcessingProcedure
from processing.procedure import Procedure

example_data = Path("seabird_example_data")
data_dir = example_data.joinpath("cnv")
raw_data_dir = example_data.joinpath("hex")
psa_dir = example_data.joinpath("psa")
target_file = data_dir.joinpath("basic_emb.cnv")
output_name = "basic_emb_4coriolis.cnv"
templates_dir = Path("templates")
config_template = templates_dir.joinpath("ctdclient.toml")
processing_template = templates_dir.joinpath("processing_template.toml")


@pytest.fixture
def processing() -> ProcessingProcedure:
    return ProcessingProcedure(processing_template)


@pytest.fixture
def simple_processing(processing: ProcessingProcedure) -> ProcessingProcedure:
    # very easy, one step processing that outputs a standard file name
    processing.procedure = Procedure(
        configuration={
            "input": [target_file],
            "output_type": "cnv",
            "output_name": output_name,
            "modules": {
                "abs_sal": {
                    "parameters": {"time": datetime.datetime.now(), "type": "ocean"}
                },
            },
        },
        auto_run=False,
    )
    processing.killed = False
    return processing


@pytest.fixture
def empty_processing(processing: ProcessingProcedure) -> ProcessingProcedure:
    # serves only as trigger for nrt pubs
    processing.procedure = Procedure(
        configuration={
            "input": [target_file],
            "output_type": "cnv",
            "output_name": str(target_file),
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
