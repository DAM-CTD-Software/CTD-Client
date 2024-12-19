from __future__ import annotations

import mimetypes
import multiprocessing as mp
import os
import platform
import re
import shutil
import smtplib
import subprocess
import time
from collections import UserList
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from email.message import EmailMessage
from pathlib import Path

import geopandas as gpd
import keyring
from code_tools.logging import get_logger
from ctdclient.definitions import cruise_head
from ctdclient.definitions import cruise_name
from ctdclient.definitions import ROOT_PATH
from ctdclient.eventmanager import EventManager
from seabirdfilehandler import SeaBirdFile
from shapely.geometry import Point
from tomlkit.toml_file import TOMLFile

logger = get_logger(__name__)


def instantiate_near_real_time_target(
    *args,
    frequency_of_action: str = "daily",
    **kwargs,
) -> NearRealTimeTarget:
    if frequency_of_action == "daily":
        class_to_instantiate = DailyPublication
    elif frequency_of_action == "each_processing":
        class_to_instantiate = EachProcessingPublication
    else:
        raise AttributeError(
            f"Unknown frequency for near-real-time publication: {
                frequency_of_action}"
        )
    return class_to_instantiate(*args, **kwargs)


class NRTList(UserList):
    def __init__(self, event_manager: EventManager):
        self.data = []
        self.event_manager = event_manager
        self.update_nrt_data()

    def update_nrt_data(self):
        for path in ROOT_PATH.glob("nrt_*.toml"):
            try:
                self.data.append(
                    instantiate_near_real_time_target(
                        **TOMLFile(path).read(),
                        file_path=path,
                        event_manager=self.event_manager,
                    )
                )
            except Exception as error:
                logger.error(
                    f"Could not instantiate nrt, using {
                        path}: {error}"
                )
                continue


class NearRealTimeTarget:
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
        target_file_directory: Path | str = "",
        geo_filter: Path | str = "",
        email_info: dict = {},
        file_path: Path | str = "",
        **kwargs,
    ):
        self.name = recipient_name
        self.address = recipient_address
        self.dir = Path(target_file_directory)
        self.suffix = target_file_suffix
        self.map_data = geo_filter
        self.email_info = email_info
        self.file_path = Path(file_path)
        self.files_already_sent = []
        self.active = True

    def _is_email(self, target: str = "") -> bool:
        """Basic check, whether we are dealing with email or not."""
        target = str(self.address) if len(target) == 0 else target
        return "@" in target

    def run(self):
        """Will move the recent files to the target location."""

    def create_email_message(
        self,
        target_files: list[Path],
        to_address: str = "",
        from_address: str = "",
        subject: str = "",
        body: str = "",
    ):
        """Creates an email with target files attached."""
        if len(target_files) == 0:
            return
        to_address = self.address if to_address == "" else to_address
        smtp_email = self.email_info["smtp_email"]
        if smtp_email.startswith("$"):
            smtp_email = os.getenv(smtp_email[1:])
        if not smtp_email:
            smtp_email = "Anonymous"
        from_address = smtp_email if from_address == "" else from_address
        subject = self.email_info["subject"] if subject == "" else subject
        body = self.email_info["body"] if body == "" else body
        timestamp = datetime.now(tz=timezone.utc).strftime("%y-%m-%d %H:%M:%S")
        msg = EmailMessage()
        msg.set_content(
            body.format(
                cruise_name=cruise_name,
                date=timestamp,
                cruise_head=cruise_head,
            )
        )

        msg["Subject"] = subject.format(
            cruise_name=cruise_name, date=timestamp
        )
        msg["From"] = from_address
        msg["To"] = to_address

        for file in target_files:
            # for some reason, one cannot attach files without specifying a
            # mime type
            mime_type, _ = mimetypes.guess_type(file)
            if mime_type is None:
                mime_type = "application/octet-stream"
            main_type, sub_type = mime_type.split("/", 1)
            with open(file, "rb") as data:
                msg.add_attachment(
                    data.read(),
                    maintype=main_type,
                    subtype=sub_type,
                    filename=file.name,
                )
        return msg

    def create_email_draft(
        self,
        msg: EmailMessage,
        file_path: Path | str = "",
    ) -> Path:
        """
        Creates an email .eml draft file, that can be opened by common email
        programs.
        """
        file_path = (
            Path(f"draft_email_to_{msg['to']}.eml")
            if file_path == ""
            else Path(file_path)
        )
        with open(file_path, "w") as f:
            f.write(msg.as_string())
        return file_path

    def open_draft_msg(self, file_path: Path | str):
        """Open an .eml file using the default email program."""
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", file_path])
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", file_path])
        else:
            raise OSError("Unsupported operating system")

    def run_email_logic(self, files_to_attach: list):
        email_message = self.create_email_message(files_to_attach)
        assert isinstance(email_message, EmailMessage)
        if self.email_info["send_directly"]:
            self.send_email(email_message)
        else:
            draft_path = self.create_email_draft(email_message)
            self.open_draft_msg(draft_path)

    def send_email(
        self,
        msg: EmailMessage,
    ):
        """
        Sends the email message using the given smtp server configuration.
        """
        try:
            smtp_server = self.email_info["smtp_server"]
            smtp_port = self.email_info["smtp_port"]
            smtp_user = self.email_info["smtp_user"]
            smtp_pass = self.email_info["smtp_pass"]
        except KeyError as error:
            logger.error(
                f"Could not send email, because of missing information: {
                    error}"
            )
            return
        if smtp_user.startswith("$"):
            smtp_user = os.getenv(smtp_user[1:])
            smtp_pass = os.getenv(smtp_pass[1:])
        else:
            smtp_user = keyring.get_password("CTD-Client", smtp_user)
            smtp_pass = keyring.get_password("CTD-Client", smtp_pass)
        if not smtp_user or not smtp_pass:
            logger.error("Could not send email: Credentials not found.")
            return
        assert isinstance(msg, EmailMessage)
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

    def copy_files(self, target_file: Path):
        """Copies target files to given location."""
        target_dir = Path(self.address)
        if not target_dir.exists():
            target_dir.mkdir(parents=True)
        source_dir = target_file.parent
        file_name = target_file.stem
        for file in source_dir.glob(f"{file_name}{self.suffix}*"):
            shutil.copy(file, target_dir)

    def get_target_files(self) -> list[Path]:
        """Creates a list of paths to files that are meant to be published."""
        target_files = []
        for file in self.dir.glob(f"*{self.suffix}.cnv"):
            # check, whether file already sent
            if file in self.files_already_sent:
                continue
            file_metadata = SeaBirdFile(file).metadata
            try:
                coordinates = (
                    self.deg_min_to_deg_decimal(file_metadata["GPS_Lon"]),
                    self.deg_min_to_deg_decimal(file_metadata["GPS_Lat"]),
                )
            except KeyError:
                coordinates = (0, 0)
            finally:
                if self.geographic_filter(coordinates):
                    target_files.append(file)
        self.files_already_sent = [*self.files_already_sent, *target_files]
        return target_files

    def deg_min_to_deg_decimal(self, value: str) -> float:
        deg, minutes, direction = re.split(r"\s+", value)
        return (float(deg) + float(minutes) / 60) * (
            -1 if direction in ["W", "S"] else 1
        )

    def geographic_filter(
        self,
        coordinate_pair: tuple,
        polygon_data_to_check_against: str = "",
    ) -> bool:
        """
        Checks, whether we are inside of a certain polygon.
        The polygon will usually be the EEZ of a certain country. Does support
        all data formats that geopandas can handle.
        """
        if len(polygon_data_to_check_against) == 0:
            polygon_data_to_check_against = str(self.map_data)
        # if no polygon is given, no geo filter can be applied and thus, we
        # just return true and skip the rest of the method
        if len(polygon_data_to_check_against) == 0:
            return True
        try:
            polygon = gpd.read_file(polygon_data_to_check_against)
            point_to_test = Point(coordinate_pair)
        except (FileNotFoundError, AttributeError):
            return False
        return polygon.contains(point_to_test)[0]


class DailyPublication(NearRealTimeTarget):
    def __init__(
        self,
        *args,
        time_to_run_at: str = "23:59:00",
        single_run: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.time_to_run_at = datetime.strptime(time_to_run_at, "%H:%M:%S")
        self.start(single_run)

    def calculate_delay(self):
        now = datetime.now()
        target_time = datetime.combine(
            date.today(), self.time_to_run_at.time()
        )
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
            self.run_email_logic(list_to_process)
        else:
            for file in list_to_process:
                # ensure, that file has been modified today
                file_modification_date = datetime.fromtimestamp(
                    file.stat().st_mtime
                ).date()
                if file_modification_date == datetime.today().date():
                    self.copy_files(file)

    def start(self, single_run: bool = False):
        self.process = mp.Process(target=self.run_task, args=(single_run,))
        self.process.start()

    def stop(self):
        self.process.kill()


class EachProcessingPublication(NearRealTimeTarget):
    def __init__(self, *args, event_manager: EventManager, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_manager = event_manager
        self.event_manager.subscribe("processing_successful", self.run)
        self.address = Path(self.address)

    def run(self, target_file: Path = Path(".")):
        if self._is_email():
            self.run_email_logic([target_file])
        else:
            self.copy_files(target_file)
