import logging
import shutil
import sys
from pathlib import Path

import requests
import xmltodict

logger = logging.getLogger(__name__)


def get_config_path(
    root_path: Path,
    ressources_path: Path,
) -> Path:
    config_name = "ctdclient.toml"
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


class Coordinates:
    def __init__(self, coordinates: tuple[str, str]):
        self.lat_in = coordinates[0]
        self.lon_in = coordinates[1]
        self.lat_min = self.parse_in(self.lat_in)
        self.lon_min = self.parse_in(self.lon_in)

    def check_deg_min(self, value: str) -> bool:
        parts = value.split()
        return parts[-1] in ["N", "W", "S", "O"]

    def min2deg(self, value: str) -> float:
        if self.check_deg_min(value):
            return self.deg_min_to_deg_decimal(value)
        else:
            return float(value)

    def deg2min(self, value: str) -> float:
        pass
