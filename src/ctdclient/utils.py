import platform
import shutil
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog as fd
from typing import Callable

import requests
import xmltodict
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
        return Path(
            shutil.copy(
                ressources_path.joinpath("templates", config_name), root_path
            )
        )
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


def individual_dship_api_call(url) -> str | None:
    """
    One single request to the API, which takes the full URL and returns
    the calls' response.
    Does also stop the API listener upon repeated failed API calls.

    Parameters
    ----------
    url : str: full URL to the specific API method with argument


    Returns
    -------
    a dictionary with the API response

    """
    try:
        response = requests.get(url, timeout=1)
    except (
        requests.exceptions.ConnectTimeout,
        requests.exceptions.ConnectionError,
        OSError,
    ):
        return None
    # handle response
    if response.status_code in ["200", 200]:
        data = response.text
        try:
            return str(xmltodict.parse(data)["sample"]["value"])
        except ValueError as error:
            logger.error(f"Could not unpack payload of call {url}: {error}")
            return None
    else:
        return None
