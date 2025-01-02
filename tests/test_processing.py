from pathlib import Path

from conftest import output_name
from conftest import target_file
from ctdclient.model.near_real_time_publication import (
    instantiate_near_real_time_target,
)
from ctdclient.model.processing import Processing
from test_near_real_time import each_processing_copy_test_info


def test_processing_canceled_run(processing: Processing):
    # interupted run
    processing.update_config("templates/processing_template.toml")
    processing.run("ctdclient.toml")
    processing.cancel()
    assert processing.killed


def test_event_processing_successful(processing: Processing):
    # uninterupted run
    processing.update_config("echo")
    processing.run("ctdclient.toml")


def test_full_procedure_with_copy_publication(simple_processing: Processing):
    instantiate_near_real_time_target(
        **each_processing_copy_test_info,
        event_manager=simple_processing.event_manager
    )
    simple_processing.run(target_file)
    expected_path = Path(
        each_processing_copy_test_info["recipient_address"]
    ).joinpath(output_name)
    if expected_path.exists():
        expected_path.unlink()
        assert True
    else:
        assert False
