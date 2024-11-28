import time
from datetime import datetime
from datetime import timedelta
from pathlib import Path

import pytest
from _pytest.capture import DontReadFromInput
from ctdclient.eventmanager import EventManager
from ctdclient.model.near_real_time_publication import DailyPublication
from ctdclient.model.near_real_time_publication import (
    EachProcessingPublication,
)
from ctdclient.model.near_real_time_publication import (
    instantiate_near_real_time_target,
)
from ctdclient.model.near_real_time_publication import NearRealTimeTarget


daily_email_test_info = {
    "recipient_name": "coriolis",
    "recipient_address": "to@example.com",
    "target_file_directory": "tests/data/out",
    "target_file_suffix": "_4coriolis",
    "frequency_of_action": "daily",
    "email_info": {
        "send_directly": True,
        "sender_address": "from@example.com",
        "subject": "CTD-Data of cruise {} on {}",
        "body": "Hello, \nthis is an automatically generated email containing the CTD data files of cruise {} from {}. If you have any questions regarding this email, do not hesitate to contact the current head of cruise {}, using {}.\n\nHave a good day!",
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

event_manager = EventManager()


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
def test_daily_call():
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
        .joinpath("test_4coriolis.cnv")
        .absolute()
    )
    assert moved_file.exists()
    moved_file.unlink()


def test_geo_filter():
    pubs = EachProcessingPublication(
        **each_processing_copy_test_info, event_manager=event_manager
    )
    assert pubs.geographic_filter((11, 54), "maps/germany.xml")
    assert not pubs.geographic_filter((50, 20), "maps/germany.xml")


def test_send_email(mocker):
    target_files = [Path(str(number)) for number in range(10)]
    mock_smtp = mocker.patch("smtplib.SMTP")
    pubs = NearRealTimeTarget(
        **daily_email_test_info,
    )
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
