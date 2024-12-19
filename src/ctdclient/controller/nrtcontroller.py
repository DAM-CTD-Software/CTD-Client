from ctdclient.controller.Controller import Controller
from ctdclient.model.near_real_time_publication import NRTList
from ctdclient.view.nrtcontrol import NRTControlFrame


class NRTController(Controller):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.model: NRTList
        self.view: NRTControlFrame

    def update(self):
        self.model.update_nrt_data()
        self.view.instantiate(self.model.data)
