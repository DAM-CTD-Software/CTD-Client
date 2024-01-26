import threading
import time
import requests
import xmltodict
import random


class DSHIPHeader:
    """
    Fetches DSHIP information via API or UDP telegram and generates
    Seabird-specific XML from that.
    """

    def __init__(
            self,
            config,
            mode='api',
            dship_url_part=':8080/dship-web/service/samples'):
        # will hold the dhsip info
        self.data: dict
        # loads the key values we want to fetch from DSHIP
        self.dict_of_samples = config['dship']['identifier']
        # vessel-specific IP, where DSHIP can be reached
        self.ip = config['dship']['ip']
        # ?
        self.dship_values = self.dict_of_samples
        # the URL of the API
        self.source = f'http:{self.ip}{dship_url_part}'
        # waiting time between two rounds of API calls
        self.fetch_timeout = config['dship']['fetch_intervall']
        # configuration file representation
        self.config = config
        # upper limit to allow for failed API calls in a row
        self.dship_fail_tolerance = 10
        # counts repeated failed API calls
        # resets to 0 upon a successfull call
        self.dship_fail_counter = 0
        # the status of the API listener
        self.alive = False
        try:
            # TODO: fix this logic...
            # TODO: and decide which way of repeatedely calling the API I
            # prefer: threading vs RepeatedTimer

            # tries a basic API call and upon failure generated dummy values,
            # as we conculde that we are not on a ship
            self.call_api(self.source, self.dict_of_samples)
        except ValueError:
            self.dummy = True
            self.generate_random_numbers()
        else:
            self.dummy = False
        finally:
            # activates the listener in any case
            self.alive = True
            self.listener = RepeatedTimer(self.fetch_timeout,
                                          self.generate_random_numbers)

    def generate_random_numbers(self):
        """A dummy number generator for GUI testing purposes."""
        for key in self.dict_of_samples:
            self.dict_of_samples[key] = random.randint(0, 100)

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
        response = requests.get(url)
        # handle response
        if response.status_code in ['200', 200]:
            data = response.text
            self.dship_fail_counter = 0
            try:
                return xmltodict.parse(data)
            except ValueError:
                return None
        else:
            if self.dship_fail_counter == self.dship_fail_tolerance:
                self.alive = False
                return None
            self.dship_fail_counter += 1
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

    def fetch(self):
        # TODO: deprecated?
        """ """
        if self.dummy:
            while self.alive:
                self.generate_random_numbers()
        else:
            while self.alive:
                self.call_api(self.source, self.dict_of_samples)

    def start_listener(self):
        """ """
        random.seed()
        self.listener_thread = threading.Timer(
            self.fetch_timeout, self.generate_random_numbers)
        # self.listener_thread.daemon = False
        self.alive = True
        self.listener_thread.start()

    def end_listener(self):
        """ """
        self.alive = False
        # self.listener_thread.cancel()
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
