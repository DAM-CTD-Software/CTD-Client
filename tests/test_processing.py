import logging
from pathlib import Path
from time import sleep

from conftest import raw_data_dir, check_and_remove_file, data_dir, output_name
from conftest import target_file
from ctdclient.definitions import CONFIG_PATH
from ctdclient.definitions import event_manager
from ctdclient.model.processing import ProcessingList
from ctdclient.model.processing import ProcessingProcedure
from ctdam.proc.procedure import Procedure

logger = logging.getLogger(__name__)


def test_processing_canceled_run(processing: ProcessingProcedure):
    # interupted run
    processing.run(Path("ctdclient.toml"))
    processing.cancel()
    assert processing.killed


def test_event_processing_successful(simple_processing: ProcessingProcedure):
    # uninterupted run
    def assert_correct_file_name(target: Path):
        assert target == target_file.absolute()

    event_manager.subscribe("processing_successful", assert_correct_file_name)
    simple_processing.run(target_file)
    sleep(4)
    assert simple_processing.process.exitcode == 0
    check_and_remove_file(data_dir.joinpath(output_name))


def test_processing_list_creation():
    proc_list = ProcessingList()
    proc_list.read_processing_files()
    assert len(proc_list) == len([file for file in CONFIG_PATH.glob('*proc*')])


def test_full_processing(processing: ProcessingProcedure):
    processing.procedure = Procedure(
        configuration={
            "modules": {
                "alignctd": {},
                "binavg": {},
            },
        },
        auto_run=False,
    )
    processing.active = True
    # proc_list = ProcessingList()
    # proc_list.data = [processing]
    input_file = raw_data_dir.joinpath("EMB356_11-1.hex")
    # proc_list.run(input_file)
    processing.run(input_file)
    while processing.process.is_alive():
        sleep(1)
    expected_file = input_file.with_suffix(".cnv")
    check_and_remove_file(expected_file)
