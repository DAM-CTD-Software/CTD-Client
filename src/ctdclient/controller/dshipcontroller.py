import time
from multiprocessing import Process
from multiprocessing import Queue
from typing import Callable
from typing import Tuple

from ctdclient.controller.Controller import Controller
from ctdclient.model.dshipcaller import DshipCaller
from ctdclient.view.dshipframe import DshipFrame
from ctdclient.view.infoframe import InfoFrame
from ctdclient.definitions import last_ctd_station

global alive
alive = True


def calling(
    method_to_call: Callable,
    fetch_intervall: int,
    queue: Queue,
    info_queue: Queue,
    debug: bool,
):
    # free function instead of class method to avoid a new class instance
    # inside of another thread
    while alive:
        dship_values = method_to_call()
        global last_ctd_station
        if debug:
            station = dship_values["Station"]
        last_ctd_station, dship_values = udpate_ctd_station(
            last_ctd_station, dship_values
        )
        debug_dship_values = dship_values
        if debug:
            debug_dship_values["Last_CTD_Station"] = last_ctd_station
            debug_dship_values["Current_Station_Read_Out"] = station
        queue.put(dship_values)
        info_queue.put(debug_dship_values)
        time.sleep(fetch_intervall)


def udpate_ctd_station(
    ctd_station: str, dship_values: dict
) -> Tuple[str, dict]:
    """
    Saves the last CTD Station and Device Action value until the next one.
    This way, other Devices do not interfere with their individual Device
    Action numbers.
    For testing reasons, an instance check is performed.
    """
    try:
        value = dship_values["Device"]
    except KeyError:
        return (ctd_station, dship_values)
    if isinstance(value, int):
        if value > 15:
            dship_values["Station"] = ctd_station
        else:
            ctd_station = str(dship_values["Station"])
    else:
        if value.lower() not in ("ctd"):
            dship_values["Station"] = ctd_station
        else:
            ctd_station = dship_values["Station"]
    return (ctd_station, dship_values)


class DshipController(Controller):

    def __init__(
        self,
        *args,
        info_frame: InfoFrame,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)
        self.model: DshipCaller
        self.view: DshipFrame
        self.info_frame = info_frame
        # sets or unsets dummy dship number generator
        if self.configuration.use_dship:
            method_to_call = self.model.call_api
        else:
            method_to_call = self.model.generate_random_numbers
        self.queue = Queue()
        self.info_queue = Queue()
        self.calling_dship = Process(
            target=calling,
            args=[
                method_to_call,
                self.configuration.dhsip_fetch_intervall,
                self.queue,
                self.info_queue,
                self.configuration.debugging,
            ],
            name="calling_dship",
            daemon=True,
        )
        self.initialize()

    def initialize(self):
        self.calling_dship.start()
        self.view.initialize(self.model.dict_of_samples, self.queue)
        self.info_frame.initialize()
        self.info_frame.update_filename(self.info_queue)

    def kill_threads(self):
        # clean up after kill signal send
        global alive
        alive = False
        self.calling_dship.terminate()
        time.sleep(self.configuration.dhsip_fetch_intervall)
        self.queue.close()
        self.queue.join_thread()
        self.calling_dship.close()


if __name__ == "__main__":
    # necessary for multithreading using multiprocessing under windows which
    # uses the 'spawn' start method
    pass
