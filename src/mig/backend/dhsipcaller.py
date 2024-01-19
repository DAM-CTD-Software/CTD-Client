import threading
import time
import requests
import xmltodict


class DSHIPHeader:

    def __init__(self, config, mode='api', dship_url_part=':8080/dship-web/service/samples'):
        self.data: dict
        self.dict_of_samples = config['dship']['identifier']
        self.ip = config['dship']['ip']
        self.dship_values = self.dict_of_samples
        self.source = f'http:{self.ip}{dship_url_part}'
        self.fetch_timeout = config['dship']['fetch_intervall']
        self.config = config
        self.dship_fail_tolerance = 10
        self.dship_fail_counter = 0
        try:
            self.call_api(self.source, self.dict_of_samples)
        except ValueError as error:
            pass
        else:
            self.alive = False
            self.start_listener()

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
        while self.alive:
            self.call_api(self.source, self.dict_of_samples)
            time.sleep(self.fetch_timeout)

    def start_listener(self):
        """ """
        self.listener_thread = threading.Thread(target=self.fetch,
                                                name='listener')
        self.listener_thread.daemon = False
        self.alive = True
        self.listener_thread.start()

    def end_listener(self):
        """ """
        self.alive = False
        self.listener_thread.join()
