import threading
import time
import requests
import xmltodict
import random


class DSHIPHeader:

    def __init__(
            self,
            config,
            mode='api',
            dship_url_part=':8080/dship-web/service/samples'):
        self.data: dict
        self.dict_of_samples = config['dship']['identifier']
        self.ip = config['dship']['ip']
        self.dship_values = self.dict_of_samples
        self.source = f'http:{self.ip}{dship_url_part}'
        self.fetch_timeout = config['dship']['fetch_intervall']
        self.config = config
        self.dship_fail_tolerance = 10
        self.dship_fail_counter = 0
        self.alive = False
        try:
            self.call_api(self.source, self.dict_of_samples)
        except ValueError:
            self.dummy = True
            self.generate_random_numbers()
        else:
            self.dummy = False
        finally:
            # self.start_listener()
            self.alive = True
            self.listener = RepeatedTimer(self.fetch_timeout,
                                          self.generate_random_numbers)

    def generate_random_numbers(self):
        for key in self.dict_of_samples:
            self.dict_of_samples[key] = random.randint(0, 100)

    def load_udp_telegram(self, port):
        import socket
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            udp_socket.bind(port)
        except (socket.error, socket.herror, TimeoutError) as error:
            pass
        else:
            data, address = udp_socket.recvfrom(1024)

    def call_api(self, url, list_of_samples, timeout=0.1):
        for sample, url_name in list_of_samples.items():
            response = self.individual_call(f'{url}/{url_name}')
            if response:
                value = response['sample']['value']
                self.dship_values[sample] = value
            time.sleep(timeout)

    def individual_call(self, url) -> dict | None:
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
        header_list = []
        for name, value in self.dship_values.items():
            header_list.append(f'** {name} = {value}')
        header_list.insert(4, f'** Operator = {operator}')
        self.config.psa.set_metadata_header(header_list)
        self.config['operators']['last'] = operator
        self.config.write()

    def fetch(self):
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

    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time.time()
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(
                self.next_call - time.time(), self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
