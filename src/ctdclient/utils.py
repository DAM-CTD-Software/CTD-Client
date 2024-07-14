import platform
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog as fd
from typing import Callable

from code_tools.logging import configure_logging
from code_tools.logging import get_logger

configure_logging("ctdclient.log")
logger = get_logger(__name__)


def get_config_path(dir_range: range = range(1, 4)) -> Path:
    if platform.system() == "Linux":
        config_name = "linux_config.toml"
    elif platform.system() == "Windows":
        config_name = "ctdclient.toml"
    else:
        logger.error("Unknown operating system. Aborting.")
        sys.exit(2)
    for dir_level in dir_range:
        dir = Path(__file__).absolute().parents[dir_level]
        file_path = dir.joinpath(config_name)
        if file_path.exists():
            return file_path
    logger.error("No configuration file found. Aborting.")
    sys.exit(1)


def select_file(
    file_type: str,
    variable: tk.StringVar,
    method_to_call: Callable | None = None,
):
    """
    Generic file selection method, that opens a file browsing pop-up.
    """
    path = Path(variable.get())
    filetypes = (
        (f"{file_type} files", f"*.{file_type}"),
        ("All files", "*.*"),
    )

    if file_type in ("psas", "xmlcons") or file_type.endswith("directory"):
        directory = fd.askdirectory(
            title=f"Path to {file_type}",
            initialdir=path,
        )
        variable.set(directory)
        if file_type == "psa_directory":
            if isinstance(method_to_call, Callable):
                method_to_call(directory)

    else:
        file = fd.askopenfilename(
            title=f"Path to {file_type}",
            initialdir=path.parent,
            initialfile=path.name,
            filetypes=filetypes,
        )
        if file:
            variable.set(file)
            return True
        else:
            return False
