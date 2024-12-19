from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.controller.Controller import Controller
from ctdclient.view.configuration import ConfigurationView
from ctdclient.view.measurement import MeasurementView


class ConfigurationController(Controller):
    def __init__(
        self,
        *args,
        measurementview: MeasurementView,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.model: ConfigurationFile
        self.view: ConfigurationView
        self.measurementview = measurementview

        # set callbacks
        self.view.base_settings.add_callback("save", self.save_configuration)

    def save_configuration(self):
        self.measurementview.info_frame.initialize()
        self.configuration.read_config()
