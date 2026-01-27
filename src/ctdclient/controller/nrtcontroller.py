from ctdclient.controller.Controller import Controller
from ctdclient.definitions import CONFIG_PATH, config
from ctdclient.model.near_real_time_publication import (
    NearRealTimeTarget,
    NRTList,
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
        self.view.add_callback("send_email", self.send_email)
        self.view.add_callback("delete_nrt", self.delete)
        self.remove_unused_keys()
        self.update()

    def remove_unused_keys(self):
        for nrt_name in list(config.near_real_time.keys()):
            if not CONFIG_PATH.joinpath(f"nrt_{nrt_name}.toml").exists():
                config.near_real_time.pop(nrt_name)

        config.write()

    def update(self):
        self.model.update_nrt_data()
        self.view.instantiate(self.model.data)

    def fetch_template(self):
        return self.model.get_template()

    def add_new_nrt_pub(self):
        return self.model.get_template()

    def toggle_activity(
        self,
        nrt: NearRealTimeTarget,
        *args,
        **kwargs,
    ):
        self.model.toggle_activity(nrt)
        self.view.toggle_activity_state(nrt, *args, **kwargs)
        config.near_real_time[nrt.name] = nrt.active
        config.write()

    def send_email(self, nrt: NearRealTimeTarget):
        files_to_attach = nrt.get_target_files()
        nrt.run_email_logic(files_to_attach=files_to_attach, run_manually=True)

    def delete(self, nrt: NearRealTimeTarget):
        self.model.delete_nrt(nrt)
        self.view.instantiate(self.model.data)
