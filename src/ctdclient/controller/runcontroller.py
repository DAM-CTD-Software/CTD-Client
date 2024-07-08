from ctdclient.controller.Controller import Controller
from ctdclient.model.fileupdater import UpdateFiles
from ctdclient.model.runseasave import RunSeasave
from ctdclient.view.measurement import MeasurementView
from ctdclient.view.runframe import RunFrame


class RunController(Controller):

    def __init__(
        self,
        *args,
        bottles,
        dship,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)
        self.view: RunFrame
        self.variables: MeasurementView = self.view.master  # pyright: ignore
        self.bottles = bottles
        self.dship = dship
        # define variables
        self.output_dir = self.configuration.output_directory
        self.last_filename = self.variables.last_filename
        self.current_filename = self.variables.current_filename
        self.cast_number = self.variables.cast_number
        self.platform = self.variables.platform
        self.operator = self.variables.operator
        self.station = self.variables.station
        # set callback methods
        self.view.add_callback("runseasave", self.run_seasave)
        self.view.add_callback("postruncheck", self.check_correct_filename)

    def run_seasave(
        self,
        file_name: str,
        downcast: bool = True,
        autostart: bool = False,
    ):
        full_file_path = self.output_dir.joinpath(file_name)
        return RunSeasave(self.configuration, full_file_path).run(
            downcast, autostart
        )

    def update_variables_post_run(self):
        self.last_filename.set(self.current_filename.get())
        self.cast_number.set(str(int(self.cast_number.get()) + 1))
        self.output_dir = self.configuration.output_directory
        self.configuration.last_platform = self.platform

    def update_variables_pre_run(self):
        self.bottles.set_psa_bottle_info()
        self.dship.build_metadata_header(
            self.platform,
            self.cast_number.get(),
            self.operator.get(),
            pos_alias=self.station.get(),
        )

    def check_correct_filename(self):
        if self.current_filename.get().split("-")[0].endswith("000"):
            self.update_file_information()

    def update_file_information(self):
        self.update_variables_post_run()
        station_and_event_info = self.dship.retrieve_station_and_event_info()
        if station_and_event_info:
            UpdateFiles(
                self.last_filename.get(),
                self.output_dir,
                station_and_event_info,
            )
