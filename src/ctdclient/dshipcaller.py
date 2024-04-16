import time
import requests
import xmltodict
import random
from functools import partial
from code_tools.logging import configure_logging, get_logger
from code_tools.repeating import RepeatedTimer

configure_logging(f"{__name__}.log")
logger = get_logger(__name__)


class DSHIPHeader:
    """
    Fetches DSHIP information via API or UDP telegram and generates
    Seabird-specific XML from that.
    """

    def __init__(
        self,
        config,
        mode="api",
        dship_url_part=":8080/dship-web/service/samples",
        dummy=False,
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
        # waiting time between two rounds of API calls
        self.fetch_timeout = config.dhsip_fetch_intervall
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
                    self.dship_values[sample] = self.format_dship_response(
                        sample, value
                    )
                except IndexError:
                    pass
                self.fail_counter = 0
                self.last_call = "successfull"
            else:
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

    def build_metadata_header(
        self,
        platform: str,
        cast: str,
        operator: str,
        pos_alias: bool = False,
        autostart: bool = False,
    ):
        """
        Generates the metadata header in the needed format and saves the last
        operator.

        Parameters
        ----------
        operator :


        Returns
        -------

        """
        header_list = []
        for name, value in self.dship_values.items():
            header_list.append(self.create_metadata_header_line(name, value))
        header_list.insert(
            2, self.create_metadata_header_line("Platform", platform)
        )
        header_list.insert(
            3, self.create_metadata_header_line("Cast", f"{int(cast):04d}")
        )
        header_list.insert(
            4, self.create_metadata_header_line("Operator", operator)
        )
        header_list.insert(
            10,
            self.create_metadata_header_line(
                "WsStartID", f"{int(cast)*25 + 1}"
            ),
        )
        if pos_alias:
            header_list[-1] = self.create_metadata_header_line(
                "Pos_Alias", pos_alias
            )
        self.config.psa.set_metadata_header(header_list, autostart)
        self.config.operators["last"] = operator
        self.config.last_cast = int(cast)
        self.config.write()
        return "\n".join(header_list)

    def create_metadata_header_line(self, name, value):
        return f"{name} = {value}"

    def format_dship_response(self, name, value):
        if name == "Station":
            try:
                _, action_log_info = value.split("_")
                station, event = action_log_info.split("-")
                formatted_value = f"{int(station):03d}-{int(event):02d}"
            except AttributeError:
                formatted_value = "000-00"
        elif name == "GPS_Lat":
            formatted_value = f"{float(value):.3f} N"
        elif name == "GPS_Lon":
            formatted_value = f"{float(value):.3f} E"
        elif name == "Echo_Depth":
            formatted_value = f"{float(value): .1f} m"
        elif name == "Air_Pressure":
            formatted_value = f"{float(value): .1f} hPa"
        else:
            formatted_value = value
        return formatted_value

    def build_file_name(self, cast_number, platform):
        cruise = self.dship_values["Cruise"]
        station = self.dship_values["Station"]
        cast_number = int(cast_number.get())
        platform_name_mapper = {
            "CTD": "CTD",
            "vCTD": "CTD",
            "sfCTD": "SF",
            "pCTD": "pCTD",
        }
        return f"{cruise}_{station}_{platform_name_mapper[platform]}_{cast_number:04d}.hex"

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
