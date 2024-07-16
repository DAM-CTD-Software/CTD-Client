from code_tools.repeating import RepeatedTimer
from ctdclient.controller.Controller import Controller
from ctdclient.model.dshipcaller import DshipCaller
from ctdclient.model.metadataheader import MetadataHeader
from ctdclient.view.dshipframe import DshipFrame
from ctdclient.view.measurement import MeasurementView


class DshipController(Controller):

    def __init__(
        self,
        *args,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)
        self.model: DshipCaller
        self.view: DshipFrame
        self.initialize()

    def initialize(self):
        self.variables: MeasurementView = self.view.master  # pyright: ignore
        self.current_filename = self.variables.current_filename
        self.cast_number = self.variables.cast_number
        self.platform = self.variables.platform
        self.view.add_callback("reconnect", self.reconnect_dship)
        self.view.initialize(self.model.dship_values)
        self.start_listener()

    def start_listener(self):
        """
        Activates the listener to periodically check for new dship values.
        """
        self.listener = RepeatedTimer(
            self.configuration.dhsip_fetch_intervall,
            self.update_dship_values,
        )

    def end_listener(self):
        """
        Ends the listener, will mostly be called when closing the program.
        """
        self.listener.stop()

    def update_dship_values(self):
        """Transfers the dship values to the main window."""
        self.view.update_dship_values(self.model.dship_values)
        if self.model.fail_counter == self.model.fail_tolerance:
            self.end_listener()
            self.view.set_dship_status_bad()
        else:
            self.view.set_dship_status_good()
        self.current_filename.set(
            MetadataHeader.build_file_name(
                self.model.dship_values,
                int(self.cast_number.get()),
                self.platform,
            )
        )

    def reconnect_dship(self):
        self.model.start_listener()
        if self.model.last_call == "successful":
            self.update_dship_values()
        self.start_listener()
