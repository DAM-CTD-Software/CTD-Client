import logging
import queue

import customtkinter as ctk
from ctdclient.definitions import config
from CTkMessagebox import CTkMessagebox


class LoggingConfig:
    def __init__(
        self,
        root: ctk.CTk | ctk.CTkToplevel | ctk.CTkFrame,
        log_file: str = "ctdclient.log",
        logger_name: str = "ctdclient",
    ):
        self.root = root
        self.log_file = log_file
        self.logger_name = logger_name
        self.configure_logging()

    def configure_logging(self):
        format = "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        loglevel = logging.DEBUG if config.debugging else logging.WARNING

        self.log_queue = queue.Queue()
        logging.basicConfig(
            level=loglevel,
            format=format,
            datefmt=datefmt,
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(),
                self.QueueHandler(self.log_queue),
            ],
        )

        self.logger = logging.getLogger(self.logger_name)
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
                    CTkMessagebox(
                        title=f"Log Message: {record.name}: {record.levelname}",
                        icon="cancel",
                        message=record.getMessage(),
                        option_1="Ok",
                    )
        except queue.Empty:
            pass
        self.root.after(1000, self.process_log_queue)
