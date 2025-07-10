import time
from datetime import datetime
from datetime import timedelta
from pathlib import Path

import pytest
from conftest import output_name
from conftest import target_file
from ctdclient.definitions import event_manager
from ctdclient.model.near_real_time_publication import DailyPublication
from ctdclient.model.near_real_time_publication import (
    EachProcessingPublication,
)
from ctdclient.model.near_real_time_publication import (
    instantiate_near_real_time_target,
)
from ctdclient.model.near_real_time_publication import NearRealTimeTarget
from ctdclient.model.processing import ProcessingProcedure


daily_email_test_info = {
    "recipient_name": "coriolis",
    "recipient_address": "to@example.com",
    "target_file_directory": "seabird_example_data/cnv",
    "target_file_suffix": "_4coriolis",
    "frequency_of_action": "daily",
    "geo_filter": "resources/maps/germany.xml",
    "email_info": {
        "send_directly": True,
        "smtp_server": "localhost",
        "smtp_port": 587,
        "smtp_email": "$MAIL",
        "smtp_user": "$IOWNAME",
        "smtp_pass": "$PASS",
        "subject": "CTD-Data of cruise {cruise_name} on {date}",
        "body": "Hello, \nthis is an automatically generated email containing the CTD data files of cruise {cruise_name} from {date}. If you have any questions regarding this email, do not hesitate to contact the current head of cruise {cruise_head}.\n\nHave a good day!",
    },
}

daily_copy_test_info = {
    "recipient_name": "something",
    "recipient_address": "tests/data/backup",
    "target_file_directory": "seabird_example_data/cnv",
    "target_file_suffix": "_4coriolis",
    "frequency_of_action": "daily",
}

each_processing_copy_test_info = {
    "recipient_name": "backup",
    "recipient_address": "tests/data/backup",
    "target_file_suffix": "_4coriolis",
    "frequency_of_action": "each_processing",
}


def test_frequency_handling():
    target = instantiate_near_real_time_target(
        **each_processing_copy_test_info,
        event_manager=event_manager,
    )
    assert isinstance(target, EachProcessingPublication)


def test_email_identification():
    assert EachProcessingPublication(
        **daily_email_test_info,
        event_manager=event_manager,
    )._is_email()


@pytest.mark.skip("fails and takes long")
def test_daily_call(fresh_target_file: Path):
    now = datetime.now()
    target = now + timedelta(seconds=1)
    DailyPublication(
        time_to_run_at=target.strftime("%H:%M:%S"),
        single_run=True,
        **daily_copy_test_info,
    )
    time.sleep(1.5)
    moved_file = (
        Path(daily_copy_test_info["recipient_address"])
        .joinpath(fresh_target_file.name)
        .absolute()
    )
    assert moved_file.exists()
    moved_file.unlink()
    fresh_target_file.unlink()


def test_geo_filter():
    pubs = EachProcessingPublication(
        **each_processing_copy_test_info, event_manager=event_manager
    )
    assert pubs.geographic_filter((11, 54), "resources/maps/germany.xml")
    assert not pubs.geographic_filter((50, 20), "resources/maps/germany.xml")


def test_send_email(mocker, fresh_target_file):
    mock_smtp = mocker.patch("smtplib.SMTP")
    pubs = NearRealTimeTarget(
        **daily_email_test_info,
    )
    target_files = pubs.get_target_files()
    msg = pubs.create_email_message(target_files)
    # test basic sending
    pubs.send_email(msg)
    mock_smtp.assert_called_once_with("localhost", 587)
    email_message_object = mock_smtp.return_value.send_message
    for attachement, file_name in zip(
        email_message_object.iter_attachements(), target_files
    ):
        assert attachement == file_name
    # test creating a draft message
    draft = pubs.create_email_draft(msg)
    assert draft.exists()
    draft.unlink()
    fresh_target_file.unlink()


def test_correct_target_files(fresh_target_file: Path):
    assert NearRealTimeTarget(**daily_copy_test_info).get_target_files() == [
        Path("seabird_example_data/cnv/test_4coriolis.cnv"),
    ]
    fresh_target_file.unlink()


@pytest.mark.seabird
def test_active_state_each_proc(simple_processing: ProcessingProcedure):
    pubs = EachProcessingPublication(
        **each_processing_copy_test_info,
    )
    # set activity to false
    pubs.active = True
    pubs.toggle_activity()
    simple_processing.run(target_file)
    expected_path = Path(each_processing_copy_test_info["recipient_address"]).joinpath(
        output_name
    )
    if expected_path.exists():
        expected_path.unlink()
        assert False
    else:
        assert True
    # set activity to true
    pubs.toggle_activity()
    simple_processing.run(target_file)
    if expected_path.exists():
        expected_path.unlink()
        assert True
    else:
        assert False
