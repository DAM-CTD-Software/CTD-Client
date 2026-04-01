import json
import logging
import random
import time

import requests

from ctdclient.definitions import config
from ctdclient.model.metadataheader import MetadataHeader
from ctdclient.utils import individual_dship_api_call

logger = logging.getLogger(__name__)


class DshipCaller:
    """
    Fetches DSHIP information via API or UDP telegram and generates
    Seabird-specific XML from that.

    Parameters
    ----------
    config: ConfigurationFile

    """

    def __init__(
        self,
        config,
    ):
        # will hold the dship info
        self.data: dict
        # loads the key values we want to fetch from DSHIP
        if config.debugging:
            extra_dict = {
                "Last_CTD_Station": "",
                "Current_Station_Read_Out": "",
            }
        else:
            extra_dict = {}
        self.dict_of_samples = {**config.dship_api_target_names, **extra_dict}
        # vessel-specific IP, where DSHIP can be reached
        self.ip = config.dship_ip
        # the values fetched from dship with corresponding header names
        self.dship_values = {}
        # the URL of the API
        self.source = f"http://{self.ip}{config.dship_url_part}"
        # configuration file representation
        self.config = config
        # counts repeated failed API calls
        # resets to 0 upon a successfull call
        self.fail_counter = 0
        # upper limit to allow for failed (individual!) API calls in a row
        self.fail_tolerance = 700
        # waiting time between two rounds of API calls
        self.fetch_timeout = config.dhsip_fetch_intervall

    def generate_random_numbers(self):
        """A dummy number generator for GUI testing purposes."""
        for key in self.dict_of_samples:
            self.dship_values[key] = random.randint(0, 100)
        self.fail_counter += 1
        if self.fail_counter == self.fail_tolerance:
            # TODO: what to do in this case?
            pass
        return self.dship_values

    def call_api(
        self,
        url: str | None = None,
        dict_of_samples: dict | None = None,
    ):
        """
        A collection of API calls according to the values in
        the dict_of_samples, which holds the names of the individual columns
        in the metadata header and their respective names in the API.

        Parameters
        ----------
        url: str | None :
            The base url of DSHIP
        dict_of_samples: dict | None :
            The DSHIP values to get

        """
        url = self.source if url is None else url
        dict_of_samples = (
            self.dict_of_samples
            if dict_of_samples is None
            else dict_of_samples
        )
        timeout = self.fetch_timeout / (len(dict_of_samples) + 1)
        for sample, url_name in dict_of_samples.items():
            response = individual_dship_api_call(f"{url}/{url_name}")
            if response:
                try:
                    self.dship_values[sample] = (
                        MetadataHeader.format_dship_response(sample, response)
                    )
                except IndexError:
                    pass
                self.fail_counter = 0
            else:
                self.dship_values[sample] = ""
                self.fail_counter += 1
                if self.fail_counter == self.fail_tolerance:
                    logger.info(
                        f"{self.fail_tolerance} failed API calls in a row."
                    )

            time.sleep(timeout)
        return self.dship_values


def get_station_log(cruise_id: str) -> None | str:
    """
    Retrieve a rudimentary ship station log via the manida DSHIP extension.

    Manida is an API-like endpoint to retrieve different ship logs from.


    Parameters
    ----------
    cruise_id: str
        The id of the current cruise

    Returns
    -------
    The API answer.

    """
    manida_url = f"http://{config.dship_ip}:8080/manida-v3/"
    station_log_url = (
        f"{manida_url}station?expeditionId={cruise_id}&format=JSON"
    )
    try:
        call = requests.get(station_log_url)
    except (
        requests.exceptions.ConnectTimeout,
        requests.exceptions.ConnectionError,
        OSError,
    ) as error:
        logger.error(f"Could not reach the manida interface: {error}")
        return None
    else:
        if call.status_code in ["200", 200]:
            return call.text
        else:
            return None


def get_ctd_last_event(station_log_json: str) -> dict:
    """
    Retrieve the last CTD station from a manida export (see get_station_log).

    Parameters
    ----------
    station_log_json: str
        A path to a manida export json file

    Returns
    -------
    The CTD station information as dictionary.
    """
    stations_info = json.loads(station_log_json)
    last_ctd_entry = {}
    for entry in stations_info["list"]:
        if entry["Device Shortname"].lower() == "ctd":
            last_ctd_entry = entry
    return last_ctd_entry


def get_station_id(event_json: dict) -> str:
    """
    Retrieve the station id from a manida export event (see get_station_log).

    Parameters
    ----------
    event_json: dict
        A single station entry from a manida export

    Returns
    -------
    The station number.
    """
    station_id = event_json["Device Operation"]
    return station_id.replace("/", "_")


def retrieve_station_and_event_info() -> str | None:
    """
    Retrieves mandia station log and extracts the last CTD station number.

    Returns
    -------
    The station number of the last CTD cast.
    """
    try:
        url_to_get_cruise_id = (
            f"{config.dship_ip}/{config.dship_api_target_names['Cruise']}"
        )
        cruise_id = individual_dship_api_call(url_to_get_cruise_id)
        station_log = get_station_log(cruise_id["sample"]["value"])
    except (KeyError, AttributeError):
        # TODO: handle this situation properly
        return None
    if station_log:
        last_event = get_ctd_last_event(station_log)
        station_event_info = get_station_id(last_event)
        if len(station_event_info) > 0:
            return station_event_info
    return None
