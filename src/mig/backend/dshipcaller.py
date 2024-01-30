import threading
import time
import requests
import xmltodict
import random
from functools import partial


class DSHIPHeader:
    """
    Fetches DSHIP information via API or UDP telegram and generates
    Seabird-specific XML from that.
    """

    def __init__(
        self,
        config,
        mode='api',
        dship_url_part=':8080/dship-web/service/samples',
        dummy=False
    ):
        # will hold the dhsip info
        self.data: dict
        # loads the key values we want to fetch from DSHIP
        self.dict_of_samples = config['dship']['identifier']
        # vessel-specific IP, where DSHIP can be reached
        self.ip = config['dship']['ip']
        # ?
        self.dship_values = self.dict_of_samples
        # the URL of the API
        self.source = f'http://{self.ip}{dship_url_part}'
        # waiting time between two rounds of API calls
        self.fetch_timeout = config['dship']['fetch_intervall']
        # configuration file representation
        self.config = config
        self.last_call = 'unsucessfull'
        # counts repeated failed API calls
        # resets to 0 upon a successfull call
        self.fail_counter = 0
        # upper limit to allow for failed (individual!) API calls in a row
        self.fail_tolerance = 70
        # the status of the API listener
        self.alive = False
        self.dummy = dummy
        self.start_listener()

    def generate_random_numbers(self):
        """A dummy number generator for GUI testing purposes."""
        for key in self.dict_of_samples:
            self.dict_of_samples[key] = random.randint(0, 100)
        self.fail_counter += 1
        if self.fail_counter == self.fail_tolerance:
            self.end_listener()
            self.last_call = 'unsucessfull'
        else:
            self.last_call = 'successfull'

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

    def call_api(
        self,
        url: str,
        dict_of_samples: dict,
        timeout: float = 0.1
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
        for sample, url_name in dict_of_samples.items():
            response = self.individual_call(f'{url}/{url_name}')
            if response:
                value = response['sample']['value']
                self.dship_values[sample] = value
                self.fail_counter = 0
                self.last_call = 'successfull'
            else:
                self.fail_counter += 1
                self.last_call = 'unsucessfull'
                if self.fail_counter == self.fail_tolerance:
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
        except requests.exceptions.ConnectTimeout:
            return None
        # handle response
        if response.status_code in ['200', 200]:
            data = response.text
            try:
                return xmltodict.parse(data)
            except ValueError:
                return None
        else:
            return None

    def build_metadata_header(self, operator):
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
            header_list.append(f'** {name} = {value}')
        header_list.insert(4, f'** Operator = {operator}')
        self.config.psa.set_metadata_header(header_list)
        self.config['operators']['last'] = operator
        self.config.write()

    def start_listener(self):
        """ """
        self.fail_counter = 0
        self.alive = True
        if self.dummy:
            method_to_call = self.generate_random_numbers
        else:
            method_to_call = partial(
                self.call_api, self.source, self.dict_of_samples)
        method_to_call()
        self.listener = RepeatedTimer(self.fetch_timeout,
                                      method_to_call)

    def end_listener(self):
        """ """
        self.alive = False
        self.listener.stop()


class RepeatedTimer(object):
    # TODO: need to transfer this into its own module
    """
    Basic implementation of a periodic method call, as the threading module
    is not super intuitive and often an overkill.
    """

    def __init__(self, interval, function, *args, **kwargs):
        self.timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time.time()
        self.start()

    def run(self):
        """ """
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        """ """
        if not self.is_running:
            self.next_call += self.interval
            self.timer = threading.Timer(
                self.next_call - time.time(), self.run)
            self.timer.start()
            self.is_running = True

    def stop(self):
        """ """
        self.timer.cancel()
        self.is_running = False
