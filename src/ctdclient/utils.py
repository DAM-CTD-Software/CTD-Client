import platform
import shutil
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog as fd
from typing import Callable

from code_tools.logging import get_logger

logger = get_logger(__name__)


def get_config_path(
    root_path: Path,
    ressources_path: Path,
) -> Path:
    if platform.system() == "Linux":
        config_name = "linux_config.toml"
    elif platform.system() == "Windows":
        config_name = "ctdclient.toml"
    else:
        sys.exit("Unknown operating system. Aborting.")
    default_file_path = root_path.joinpath(config_name)
    if default_file_path.exists():
        return default_file_path
    try:
        logger.warning("Using template configuration file.")
        return Path(shutil.copy(
            ressources_path.joinpath("templates", config_name), root_path
        ))
    except FileNotFoundError:
        sys.exit("No configuration file found. Aborting.")


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
