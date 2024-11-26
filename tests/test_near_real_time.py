from pathlib import Path
from datetime import datetime, timedelta
import time
from ctdclient.eventmanager import EventManager
from ctdclient.model.near_real_time_publication import DailyPublication, EachProcessingPublication, instantiate_near_real_time_target


daily_email_test_info = {
    'recipient_name': "coriolis",
    'recipient_address': "codata@ifremer.fr",
    'target_file_directory': "tests/data/out",
    'target_file_suffix': "_4coriolis",
    'frequency_of_action': "daily",
}

daily_copy_test_info = {
    'recipient_name': "something",
    'recipient_address': "tests/data/backup",
    'target_file_directory': "seabird_example_data/cnv",
    'target_file_suffix': "_4coriolis",
    'frequency_of_action': "daily",
}

each_processing_copy_test_info = {
    'recipient_name': "backup",
    'recipient_address': "tests/data/backup",
    'target_file_suffix': "_4coriolis",
    'frequency_of_action': "each_processing",
}

event_manager = EventManager()


def test_frequency_handling():
    target = instantiate_near_real_time_target(
        **each_processing_copy_test_info, event_manager=event_manager,
    )
    assert isinstance(target, EachProcessingPublication)


def test_email_identification():
    assert EachProcessingPublication(
        **daily_email_test_info, event_manager=event_manager,)._is_email()


def test_daily_call():
    now = datetime.now()
    target = now + timedelta(seconds=1)
    DailyPublication(
        time_to_run_at=target.strftime('%H:%M:%S'),
        single_run=True,
        **daily_copy_test_info,
    )
    time.sleep(1.5)
    moved_file = Path(daily_copy_test_info['recipient_address']).joinpath(
        'basic_emb_4coriolis.cnv')
    assert moved_file.exists()
    moved_file.unlink()


def test_geo_filter():
    pubs = EachProcessingPublication(
        **each_processing_copy_test_info, event_manager=event_manager)
    assert pubs.geographic_filter((11, 54), 'maps/germany.xml')
    assert not pubs.geographic_filter((50, 20), 'maps/germany.xml')
