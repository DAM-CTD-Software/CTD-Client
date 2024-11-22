from __future__ import annotations
from abc import ABC
from pathlib import Path
from datetime import datetime, timedelta, date
import shutil
import multiprocessing as mp
import time
from code_tools.logging import get_logger

from ctdclient.eventmanager import EventManager

logger = get_logger(__name__)


def instantiate_near_real_time_target(
    *args,
    frequency_of_action: str = 'daily',
    **kwargs,
) -> NearRealTimeTarget:
    if frequency_of_action == 'daily':
        class_to_instantiate = DailyPublication
    elif frequency_of_action == 'each_processing':
        class_to_instantiate = EachProcessingPublication
    else:
        raise AttributeError(
            f"Unknown frequency for near-real-time publication: {
                frequency_of_action}")
    return class_to_instantiate(
        *args,
        **kwargs
    )


class NearRealTimeTarget(ABC):
    """
    Stores information for near-real-time distribution of latest CTD data files.
    Can work in two modes: email or rsync/copy. Will distinguish between these
    by checking 'recipient_adress' for an '@'.
    """

    def __init__(
        self,
        recipient_name: str,
        recipient_address: str,
        target_file_suffix: str,
        target_file_directory: Path | str = '',
        **kwargs,
    ):
        self.name = recipient_name
        self.address = recipient_address
        self.dir = Path(target_file_directory)
        self.suffix = target_file_suffix
        self.files_already_sent = []

    def _is_email(self, target: str = "") -> bool:
        """Basic check, whether we are dealing with email or not."""
        target = str(self.address) if len(target) == 0 else target
        return '@' in target

    def run(self):
        """Will move the recent files to the target location."""

    def send_email(self, target_files: list[Path]):
        """Sends an email with target files to the given address."""
        # TODO: implement

    def copy_files(self, target_file: Path):
        """Copies target files to given location."""
        target_dir = Path(self.address)
        if not target_dir.exists():
            target_dir.mkdir(parents=True)
        source_dir = target_file.parent
        file_name = target_file.stem
        for file in source_dir.glob(f'{file_name}{self.suffix}*'):
            shutil.copy(file, target_dir)

    def get_target_files(self) -> list[Path]:
        """Creates a list of paths to files that are meant to be published."""
        target_files = [
            file
            for file in self.dir.iterdir()
            if file not in self.files_already_sent
        ]
        self.files_already_sent = [*self.files_already_sent, *target_files]
        return target_files


class DailyPublication(NearRealTimeTarget):

    def __init__(
        self,
        *args,
        time_to_run_at: str = '23:59:00',
        single_run: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.time_to_run_at = datetime.strptime(time_to_run_at, "%H:%M:%S")
        self.start(single_run)

    def calculate_delay(self):
        now = datetime.now()
        target_time = datetime.combine(
            date.today(), self.time_to_run_at.time())
        if now > target_time:
            # move target time to the next day
            target_time += timedelta(days=1)
        return (target_time - now).total_seconds()

    def run_task(self, single_run: bool = False):
        while True:
            time.sleep(self.calculate_delay())
            self.action()
            if single_run:
                break

    def action(self):
        list_to_process = self.get_target_files()
        if len(list_to_process) == 0:
            return
        if self._is_email():
            self.send_email(list_to_process)
        else:
            for file in list_to_process:
                # ensure, that file has been modified today
                file_modification_date = datetime.fromtimestamp(
                    file.stat().st_mtime).date()
                if file_modification_date == datetime.today().date():
                    self.copy_files(file)

    def start(self, single_run: bool = False):
        self.process = mp.Process(target=self.run_task, args=(single_run,))
        self.process.start()

    def stop(self):
        self.process.kill()


class EachProcessingPublication(NearRealTimeTarget):

    def __init__(self, *args, event_manager: EventManager, ** kwargs):
        super().__init__(*args, **kwargs)
        self.event_manager = event_manager
        self.event_manager.subscribe(
            'processing_successful', self.run
        )
        self.address = Path(self.address)

    def run(self, target_file: Path = Path('.')):
        if self._is_email():
            pass
        else:
            self.copy_files(target_file)
