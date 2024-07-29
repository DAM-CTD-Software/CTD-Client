import time
from multiprocessing import Process
from multiprocessing import Queue
from typing import Callable

from ctdclient.controller.Controller import Controller
from ctdclient.model.dshipcaller import DshipCaller
from ctdclient.view.dshipframe import DshipFrame
from ctdclient.view.infoframe import InfoFrame


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
        if self.configuration.use_dship:
            method_to_call = self.model.call_api
        else:
            method_to_call = self.model.generate_random_numbers
        self.queue = Queue()
        self.info_queue = Queue()
        self.calling_dship = Process(
            target=self.calling,
            args=[method_to_call],
            name="calling_dship",
            daemon=False,
        )
        self.initialize()

    def initialize(self):
        self.alive = True
        self.calling_dship.start()
        self.view.initialize(self.model.dship_values, self.queue)
        self.info_frame.initialize(self.info_queue)

    def calling(self, method_to_call: Callable):
        while self.alive:
            method_to_call()
            self.queue.put(self.model.dship_values)
            self.info_queue.put(self.model.dship_values)
            time.sleep(self.configuration.dhsip_fetch_intervall)

    def kill_threads(self):
        # clean up after kill signal send
        self.alive = False
        self.calling_dship.terminate()
        time.sleep(self.configuration.dhsip_fetch_intervall)
        self.queue.close()
        self.queue.join_thread()
        self.calling_dship.close()
