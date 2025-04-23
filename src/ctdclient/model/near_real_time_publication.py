from __future__ import annotations

import logging
import mimetypes
import multiprocessing as mp
import os
import platform
import re
import shutil
import smtplib
import subprocess
import time
from abc import abstractmethod
from collections import UserList
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Callable

import geopandas as gpd
from ctdclient.definitions import config
from ctdclient.definitions import cruise_head
from ctdclient.definitions import cruise_name
from ctdclient.definitions import event_manager
from ctdclient.definitions import ROOT_PATH
from ctdclient.definitions import TEMPLATE_PATH
from seabirdfilehandler import SeaBirdFile
from shapely.geometry import Point
from tomlkit.toml_file import TOMLFile

logger = logging.getLogger(__name__)


def instantiate_near_real_time_target(
    *args,
    frequency_of_action: str = "23:59:00",
    **kwargs,
) -> NearRealTimeTarget:
    if ":" in frequency_of_action:
        class_to_instantiate = DailyPublication
        kwargs["time_to_run_at"] = frequency_of_action
    elif frequency_of_action == "each_processing":
        class_to_instantiate = EachProcessingPublication
    else:
        raise AttributeError(
            f"Unknown frequency for near-real-time publication: {frequency_of_action}"
        )
    return class_to_instantiate(*args, **kwargs)


class NRTList(UserList):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = []

    def update_nrt_data(self, clear_data: bool = True):
        if clear_data:
            self.kill_processes()
            self.data = []
        # TODO: make this flexible? eg allow dir selection
        for path in ROOT_PATH.glob("nrt_*.toml"):
            try:
                self.data.append(self.create_nrt_instance(path))
            except Exception as error:
                logger.error(
                    f"Could not instantiate nrt, using {path}: {error}"
                )
                continue

    def create_nrt_instance(self, path: Path):
        toml_file = TOMLFile(path).read()
        name = toml_file["recipient_name"]
        active = (
            config.near_real_time[name]
            if name in config.near_real_time
            else False
        )
        return instantiate_near_real_time_target(
            **toml_file,
            file_path=path,
            active=active,
        )

    def get_template(
        self, template_path: Path = TEMPLATE_PATH.joinpath("nrt_template.toml")
    ):
        if not template_path.exists():
            return None
        template = self.create_nrt_instance(template_path)
        self.data.append(template)
        return template

    def toggle_activity(self, nrt: NearRealTimeTarget):
        if nrt in self.data:
            nrt.toggle_activity()

    def kill_processes(self):
        for nrt in self.data:
            if isinstance(nrt, DailyPublication):
                nrt.stop()

    def delete_nrt(self, nrt: NearRealTimeTarget):
        self.data.remove(nrt)
        if isinstance(nrt, DailyPublication):
            nrt.stop()
        if nrt.file_path.exists():
            nrt.file_path.unlink()
        config.near_real_time.pop(nrt.name)
        config.write()


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
        active: bool = False,
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
        self.active = active

    @abstractmethod
    def toggle_activity(self):
        pass

    def _is_email(self, target: str = "") -> bool:
        """Basic check, whether we are dealing with email or not."""
        target = str(self.address) if len(target) == 0 else target
        return "@" in target

    @abstractmethod
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
            cruise_name=cruise_name,
            date=timestamp,
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
        msg.add_header("X-Unsent", "1")
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

    def run_email_logic(
        self,
        files_to_attach: list,
        run_manually: bool = False,
    ):
        if not run_manually and len(files_to_attach) == 0:
            logger.info(
                "Automatic email not sent because no files are available."
            )
            return
        email_message = self.create_email_message(files_to_attach)
        open_draft = True if self.email_info["open_draft"] == "true" else False
        if run_manually or open_draft:
            draft_path = self.create_email_draft(email_message)
            self.open_draft_msg(draft_path)
        else:
            self.send_email(email_message)

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
        except KeyError as error:
            logger.error(
                f"Could not send email, because of missing information: {error}"
            )
            return
        assert isinstance(msg, EmailMessage)
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            try:
                server.send_message(msg)
            except smtplib.SMTPRecipientsRefused as error:
                logger.error(f"Credentials needed to send email: {error}")
            else:
                logger.info(f"Email sent to {msg['To']}")

    def copy_files(self, target_file: Path):
        """Copies target files to given location."""
        target_dir = Path(self.address)
        if not target_dir.exists():
            target_dir.mkdir(parents=True)
        source_dir = target_file.parent
        file_name = target_file.stem
        for file in source_dir.glob(f"{file_name}{self.suffix}*"):
            shutil.copy(file, target_dir)
            logger.info(f"Copied {file} to {target_dir}")

    def get_target_files(self, target_file: Path = Path(".")) -> list[Path]:
        """Creates a list of paths to files that are meant to be published."""
        file_name = "" if target_file == Path(".") else str(target_file.stem)
        target_files = []
        for file in self.dir.glob(f"*{file_name}{self.suffix}*"):
            # check, whether file already sent
            if (
                (file in self.files_already_sent)
                or (file.is_dir())
                or (file.name.startswith("."))
            ):
                continue
            if len(self.map_data) > 0:
                try:
                    file_metadata = SeaBirdFile(
                        path_to_file=file,
                        only_header=True,
                    ).metadata
                except PermissionError as error:
                    message = (
                        f"Insufficient permissions to read {file}: {error}"
                    )
                    logger.error(message)
                else:
                    try:
                        coordinates = (
                            self.deg_min_to_deg_decimal(
                                file_metadata["GPS_Lon"]
                            ),
                            self.deg_min_to_deg_decimal(
                                file_metadata["GPS_Lat"]
                            ),
                        )
                    except (KeyError, ValueError):
                        coordinates = (0, 0)
                    finally:
                        if not self.geographic_filter(coordinates):
                            continue

            if self.time_filter(file):
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

    def time_filter(self, file: Path) -> bool:
        """Ensure, that file has been modified in the last 24 hours."""
        last_twenty_four_hours = datetime.now() + timedelta(days=-1)
        file_modification_time = datetime.fromtimestamp(file.stat().st_mtime)
        return datetime.now() > file_modification_time > last_twenty_four_hours


class DailyPublication(NearRealTimeTarget):
    def __init__(
        self,
        *args,
        time_to_run_at: str = "23:59:30",
        single_run: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.single_run = single_run
        try:
            self.time_to_run_at = datetime.strptime(time_to_run_at, "%H:%M:%S")
        except ValueError:
            logger.error(f"Could not parse the given time: {time_to_run_at}")
        if self.active:
            self.start()

    def action(self):
        list_to_process = self.get_target_files()
        if self._is_email():
            self.run_email_logic(list_to_process)
        else:
            for file in list_to_process:
                self.copy_files(file)

    def start(self):
        self.process = mp.Process(
            target=timer,
            args=[self.time_to_run_at, self.action, self.single_run],
        )
        self.process.start()

    def stop(self):
        try:
            self.process.terminate()
            self.process.join(timeout=2)
        except AttributeError:
            pass

    def toggle_activity(self):
        self.active = not self.active
        if self.active:
            self.start()
        else:
            self.stop()


def timer(time_to_run_at: datetime, function: Callable, single_run: bool):
    def calculate_delay():
        now = datetime.now()
        target_time = datetime.combine(date.today(), time_to_run_at.time())
        if now > target_time:
            # move target time to the next day
            target_time += timedelta(days=1)
        delay = (target_time - now).total_seconds()
        return delay

    time_left = calculate_delay()
    while True:
        time.sleep(1)
        time_left -= 1
        if time_left <= 0:
            function()
            if single_run:
                break
            time_left = calculate_delay()


class EachProcessingPublication(NearRealTimeTarget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.active:
            event_manager.subscribe("processing_successful", self.run)
        self.address = Path(self.address)

    def toggle_activity(self):
        self.active = not self.active
        if self.active:
            event_manager.subscribe("processing_successful", self.run)
        else:
            event_manager.unsubscribe("processing_successful", self.run)

    def run(self, target: Path = Path(".")):
        target_files = self.get_target_files(target)
        if self._is_email():
            self.run_email_logic(target_files)
        else:
            self.copy_files(target)
