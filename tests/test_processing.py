from pathlib import Path
from processing.procedure import Procedure
import pytest
from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.eventmanager import EventManager
from ctdclient.model.near_real_time_publication import instantiate_near_real_time_target
from ctdclient.model.processing import Processing
from test_near_real_time import each_processing_copy_test_info

target_file = Path('seabird_example_data/cnv/basic_emb.cnv')


def _help(*args, **kwargs):
    assert True


@pytest.fixture
def processing() -> Processing:
    config = ConfigurationFile("templates/ctdclient.toml")
    event_manager = EventManager()
    event_manager.subscribe("processing_successful", _help)
    return Processing(config, event_manager)


def test_processing_canceled_run(processing: Processing):
    # interupted run
    processing.update_config('templates/processing_template.toml')
    processing.run('ctdclient.toml')
    processing.cancel()
    assert processing.killed


def test_event_processing_successful(processing: Processing):
    # uninterupted run
    processing.update_config('echo')
    processing.run('ctdclient.toml')


def test_full_procedure_with_copy_publication(processing: Processing):
    instantiate_near_real_time_target(
        **each_processing_copy_test_info,
        event_manager=processing.event_manager
    )
    output_name = 'basic_emb_4coriolis.cnv'
    processing.procedure = Procedure(
        configuration={
            "input": [target_file],
            "output_type": "cnv",
            'output_name': output_name,
            "modules": {
                "abs_sal": {},
            },
        },
        auto_run=False,
    )
    processing.current_config = Path('templates/processing_template.toml')
    processing.killed = False
    processing.run(target_file)
    expected_path = Path(each_processing_copy_test_info['recipient_address']).joinpath(
        output_name)
    if expected_path.exists():
        expected_path.unlink()
        assert True
    else:
        assert False
