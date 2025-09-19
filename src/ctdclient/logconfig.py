import logging
import mimetypes
import queue
import smtplib
import sys
from datetime import datetime
from datetime import timezone
from email.message import EmailMessage
from pathlib import Path

import customtkinter as ctk
from ctdclient.definitions import config
from ctdclient.definitions import cruise_name
from CTkMessagebox import CTkMessagebox
from platformdirs import user_log_dir


class LoggingConfig:
    def __init__(
        self,
        root: ctk.CTk | ctk.CTkToplevel | ctk.CTkFrame,
        logger_name: str = "ctdclient",
    ):
        self.root = root
        self.log_file = Path(user_log_dir("ctdclient")).joinpath(
            "ctdclient.log"
        )
        if not self.log_file.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger_name = logger_name
        self.configure_logging()

    def configure_logging(self):
        # need to explicetly set PIL log level, as it heavily spams when using
        # debug log level
        logging.getLogger("PIL").setLevel(logging.WARNING)
        format = "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        loglevel = logging.DEBUG if config.debugging else logging.WARNING

        self.log_queue = queue.Queue()
        logging.basicConfig(
            level=loglevel,
            format=format,
            datefmt=datefmt,
            handlers=[logging.FileHandler(self.log_file)],
        )

        self.logger = logging.getLogger(self.logger_name)
        # log to console when not running as exe
        if getattr(sys, "frozen", True):
            sh = logging.StreamHandler()
            sh.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(name)s - %(message)s")
            sh.setFormatter(formatter)
            logging.getLogger("").addHandler(sh)
        # log to GUI with restricted log level
        qh = self.QueueHandler(self.log_queue)
        qh.setLevel(logging.DEBUG if config.debugging else logging.ERROR)
        logging.getLogger("").addHandler(qh)
        self.root.after(1000, self.process_log_queue)

    class QueueHandler(logging.Handler):
        """Custom logging handler that puts log records into a queue."""

        def __init__(self, log_queue):
            super().__init__()
            self.log_queue = log_queue

        def emit(self, record):
            self.log_queue.put(record)

    def process_log_queue(self):
        """Process log messages from the queue and display them in a messagebox."""
        try:
            while True:
                record = self.log_queue.get(block=False)
                if record:
                    answer = CTkMessagebox(
                        title=f"Log Message: {record.name}: {record.levelname}",
                        icon="cancel",
                        message=record.getMessage(),
                        option_1="Ok",
                        option_2="Send as email",
                    )
                    if answer.get() == "Send as email":
                        self.send_email(record)
        except queue.Empty:
            pass
        self.root.after(1000, self.process_log_queue)

    def send_email(self, record):
        try:
            smtp_server = config.email_config["smtp_server"]
            smtp_port = config.email_config["smtp_port"]
            assert len(smtp_server) and len(str(smtp_port))
            server = smtplib.SMTP(smtp_server, int(smtp_port))
        except (KeyError, AssertionError):
            CTkMessagebox(
                title="No email server configured",
                icon="cancel",
                message="Cannot send email, you need to configure the email settings in the Settings correctly.",
                option_1="Ok",
            )
            self.logger.error(
                "Could not send email, because of missing smtp server and/or port information."
            )
            return
        except ConnectionRefusedError:
            CTkMessagebox(
                title="Could not reach email server",
                icon="cancel",
                message="Cannot send email, as the server refuses a connection",
                option_1="Ok",
            )
            self.logger.error(
                "Could not send email, because of wrong smtp server and/or port information."
            )
            return

        msg = EmailMessage()
        timestamp = datetime.now(tz=timezone.utc).strftime("%y-%m-%d %H:%M:%S")
        msg.set_content(
            f"{timestamp} - {record.name} - {record.levelname} - {record.getMessage()}"
        )
        msg["Subject"] = f"CTD-Client Error Log from {cruise_name}"
        msg["From"] = config.email_config["smtp_email"]
        msg["To"] = "emil.michels@io-warnemuende.de"
        for file in ["ctdclient.toml", "ctdclient.log"]:
            try:
                mime_type, _ = mimetypes.guess_type(file)
                if mime_type is None:
                    mime_type = "application/octet-stream"
                main_type, sub_type = mime_type.split("/", 1)
                with open(file, "rb") as data:
                    msg.add_attachment(
                        data.read(),
                        maintype=main_type,
                        subtype=sub_type,
                        filename=file,
                    )
            except Exception:
                continue
        server.starttls()
        try:
            server.send_message(msg)
        except smtplib.SMTPRecipientsRefused as error:
            self.logger.error(f"Credentials needed to send email: {error}")
        else:
            self.logger.info(f"Email sent to {msg['To']}")
