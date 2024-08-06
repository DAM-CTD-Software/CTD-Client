import time
from multiprocessing import Process
from multiprocessing import Queue
from typing import Callable

from ctdclient.controller.Controller import Controller
from ctdclient.model.dshipcaller import DshipCaller
from ctdclient.view.dshipframe import DshipFrame
from ctdclient.view.infoframe import InfoFrame

global alive
alive = True

def calling(
        method_to_call: Callable,
        fetch_intervall: int,
        queue: Queue,
        info_queue: Queue,
        ):
    # free function instead of class method to avoid a new class instance inside of another thread
    while alive:
        dship_values = method_to_call()
        queue.put(dship_values)
        info_queue.put(dship_values)
        time.sleep(fetch_intervall)


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
            args=[method_to_call, self.configuration.dhsip_fetch_intervall, self.queue, self.info_queue, self.model],
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
    # necessary for multithreading using multiprocessing under windows which uses the 'spawn' start method
    pass