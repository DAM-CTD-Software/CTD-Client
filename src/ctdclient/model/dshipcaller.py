import json
import random
import time
from functools import partial

import requests
import xmltodict
from code_tools.logging import get_logger
from code_tools.repeating import RepeatedTimer
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
        dummy=True,
    ):
        # will hold the dhsip info
        self.data: dict
        # loads the key values we want to fetch from DSHIP
        self.dict_of_samples = config.dship_api_target_names
        # vessel-specific IP, where DSHIP can be reached
        self.ip = config.dship_ip
        # the values fetched from dship with corresponding header names
        self.dship_values = {}
        # the URL of the API
        self.source = f"http://{self.ip}{dship_url_part}"
        # configuration file representation
        self.config = config
        self.last_call = "unsucessfull"
        # counts repeated failed API calls
        # resets to 0 upon a successfull call
        self.fail_counter = 0
        # upper limit to allow for failed (individual!) API calls in a row
        self.fail_tolerance = 700
        # the status of the API listener
        self.alive = False
        # waiting time between two rounds of API calls
        fetch_timeout = config.dhsip_fetch_intervall
        # 0 is a flag for testing purposes
        self.fetch_timeout = fetch_timeout
        self.dummy = dummy
        self.start_listener()

    def generate_random_numbers(self):
        """A dummy number generator for GUI testing purposes."""
        for key in self.dict_of_samples:
            self.dship_values[key] = random.randint(0, 100)
        self.fail_counter += 1
        if self.fail_counter == self.fail_tolerance:
            self.end_listener()
            self.last_call = "unsucessfull"
        else:
            self.last_call = "successfull"

    def load_udp_telegram(self, port):
        # TODO: finish this
        """
        Collects a udp telegram the ship provides.

        Parameters
        ----------
        port :


        Returns
        -------

        """
        import socket

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            udp_socket.bind(port)
        except (socket.error, socket.herror, TimeoutError) as error:
            pass
        else:
            data, address = udp_socket.recvfrom(1024)

    def call_api(self, url: str, dict_of_samples: dict):
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
                self.last_call = "successfull"
            else:
                self.dship_values[sample] = ""
                self.fail_counter += 1
                self.last_call = "unsucessfull"
                if self.fail_counter == self.fail_tolerance:
                    logger.info(
                        f"{self.fail_tolerance} failed API calls in a row."
                    )
                    self.end_listener()

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

    def start_listener(self):
        """ """
        self.fail_counter = 0
        self.alive = True
        if self.dummy:
            method_to_call = self.generate_random_numbers
        else:
            method_to_call = partial(
                self.call_api, self.source, self.dict_of_samples
            )
        method_to_call()
        self.listener = RepeatedTimer(self.fetch_timeout, method_to_call)

    def end_listener(self):
        """ """
        self.alive = False
        self.listener.stop()

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
