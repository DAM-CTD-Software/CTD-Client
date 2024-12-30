from ctdclient.controller.Controller import Controller
from ctdclient.model.near_real_time_publication import (
    NRTList,
    NearRealTimeTarget,
)
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
        self.view.add_callback("get_template", self.fetch_template)
        self.view.add_callback("new_nrt", self.add_new_nrt_pub)
        self.view.add_callback("update_nrts", self.update)
        self.view.add_callback("toggle_activity", self.toggle_activity)
        self.update()

    def update(self):
        self.model.update_nrt_data()
        self.view.instantiate(self.model.data)

    def fetch_template(self):
        return self.model.template

    def add_new_nrt_pub(self):
        return self.model.template

    def toggle_activity(
        self,
        nrt: NearRealTimeTarget,
        *args,
        **kwargs,
    ):
        self.model.toggle_activity(nrt)
        self.view.toggle_activity_state(nrt, *args, **kwargs)
