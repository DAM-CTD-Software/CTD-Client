import logging
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import requests
import tomlkit
import xmltodict
from tomlkit.toml_file import TOMLFile

logger = logging.getLogger(__name__)


def get_config_path(
    root_path: Path,
    template_path: Path,
) -> Path:
    config_name = "ctdclient.toml"
    default_file_path = root_path.joinpath(config_name)
    if default_file_path.exists():
        return default_file_path
    try:
        logger.warning("Using template configuration file.")
        default_file_path.parent.mkdir(parents=True, exist_ok=True)
        return Path(
            shutil.copy(template_path.joinpath(config_name), default_file_path)
        )
    except FileNotFoundError:
        sys.exit("No configuration file found. Aborting.")


def create_new_config_file(old_config: Path, new_config: Path) -> dict:
    old = TOMLFile(old_config).read()
    new = TOMLFile(new_config).read()
    _merge_dicts(old, new)
    with open(old_config, "w") as file:
        file.write(tomlkit.dumps(old).replace("\r", ""))
    return old


def _merge_dicts(original, new):
    if isinstance(original, dict) and isinstance(new, dict):
        original_keys = set(original.keys())
        new_keys = set(new.keys())
        different_keys = new_keys - original_keys

        for key in different_keys:
            original[key] = new[key]

        for key in original_keys & new_keys:
            _merge_dicts(original[key], new[key])
    elif isinstance(original, list) and isinstance(new, list):
        for i in range(min(len(original), len(new))):
            _merge_dicts(original[i], new[i])
        if len(new) > len(original):
            original.extend(new[len(original) :])
    else:
        pass


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


def call_editor(file_path: Path):
    try:
        if platform.system() == "Windows":
            try:
                os.startfile(file_path)
            except OSError:
                # if default association fails, use notepad
                subprocess.Popen(["notepad.exe", file_path])
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", file_path])
        elif platform.system() == "Linux":
            editor = os.environ.get("EDITOR", "/usr/bin/vim")
            subprocess.Popen([editor, file_path])
        else:
            raise OSError("Unsupported operating system")
    except Exception as error:
        logger.error(f"Could not open {file_path}: {error}")
