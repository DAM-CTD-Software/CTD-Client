from pathlib import Path

import pytest
from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.model.processing import ProcessingProcedure
from processing.procedure import Procedure

example_data = Path("seabird_example_data")
data_dir = example_data.joinpath("cnv")
raw_data_dir = example_data.joinpath("hex")
psa_dir = example_data.joinpath("psa")
target_file = data_dir.joinpath("multiple_soaking.cnv")
output_name = "basic_emb_4coriolis.cnv"
templates_dir = Path("resources/templates")
config_template = templates_dir.joinpath("ctdclient.toml")
processing_template = templates_dir.joinpath("processing_template.toml")


def pytest_addoption(parser):
    """
    Adds a command line option to pytest that controls the skipping of code
    that runs seabird processing modules.
    """
    parser.addoption(
        "--run_seabird",
        "-S",
        action="store_true",
        default=False,
        help="Whether to run seabird processing modules during the tests.",
    )


@pytest.fixture
def run_seabird_modules(request) -> bool:
    """
    Makes the boolean flag of the command line option available to individual
    tests.
    """
    return request.config.getoption("--run_seabird")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run_seabird"):
        return
    skip_non_seabird = pytest.mark.skip(reason="No seabird option given.")
    for item in items:
        if "seabird" in item.keywords:
            item.add_marker(skip_non_seabird)


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
                "alignctd": {
                    "sbeox0ML/L": None,
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

@pytest.fixture
def config() -> ConfigurationFile:
    return ConfigurationFile(config_template)
