import json
import random
import time

import requests
import xmltodict
from code_tools.logging import get_logger
from ctdclient.model.metadataheader import MetadataHeader

logger = get_logger(__name__)


class DshipCaller:
    """
    Fetches DSHIP information via API or UDP telegram and generates
    Seabird-specific XML from that.
    """

    def __init__(
        self,
        config,
        dship_url_part=":8080/dship-web/service/samples",
    ):
        # will hold the dship info
        self.data: dict
        # loads the key values we want to fetch from DSHIP
        self.dict_of_samples = config.dship_api_target_names
        # vessel-specific IP, where DSHIP can be reached
        self.ip = config.dship_ip
        # the values fetched from dship with corresponding header names
        self.dship_values = self.dict_of_samples
        # the URL of the API
        self.source = f"http://{self.ip}{dship_url_part}"
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
        url :

        dict_of_samples :

        timeout :
             (Default value = 0.1)

        Returns
        -------

        """
        url = self.source if url is None else url
        dict_of_samples = (
            self.dict_of_samples
            if dict_of_samples is None
            else dict_of_samples
        )
        timeout = self.fetch_timeout / (len(dict_of_samples) + 1)
        for sample, url_name in dict_of_samples.items():
            response = self.individual_call(f"{url}/{url_name}")
            if response:
                value = response["sample"]["value"]
                try:
                    self.dship_values[sample] = (
                        MetadataHeader.format_dship_response(sample, value)
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

    def individual_call(self, url) -> dict | None:
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
                return xmltodict.parse(data)
            except ValueError as error:
                logger.error(
                    f"Could not unpack payload of call {url}: {error}"
                )
                return None
        else:
            return None

    def get_station_log(self, cruise_id: str) -> None | str:
        manida_url = "http://dship1:8080/manida-v3/"
        station_log_url = f"{manida_url}station?expeditionId={
            cruise_id}&format=JSON"
        try:
            call = requests.get(station_log_url)
        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            OSError,
        ):
            return None
        else:
            if call.status_code in ["200", 200]:
                return call.text
            else:
                return None

    def get_ctd_last_event(self, station_log_json: str) -> dict:
        stations_info = json.loads(station_log_json)
        last_ctd_entry = {}
        for entry in stations_info["list"]:
            if entry["Device"] == "CTD":
                last_ctd_entry = entry
        return last_ctd_entry

    def get_station_id(self, event_json: dict) -> str:
        station_id = event_json["Device Operation"]
        return station_id.replace("/", "_")

    def retrieve_station_and_event_info(self) -> str | None:
        station_log = self.get_station_log(self.dship_values["Cruise"])
        if station_log:
            last_event = self.get_ctd_last_event(station_log)
            station_event_info = self.get_station_id(last_event)
            if len(station_event_info) > 0:
                return station_event_info
        return None
