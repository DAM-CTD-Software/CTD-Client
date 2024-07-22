from pathlib import Path

from ctdclient.controller.Controller import Controller
from ctdclient.model.fileupdater import UpdateFiles
from ctdclient.model.metadataheader import MetadataHeader
from ctdclient.model.processing import WindowsBatch
from ctdclient.model.runseasave import RunSeasave
from ctdclient.view.measurement import MeasurementView
from ctdclient.view.runframe import RunFrame


class RunController(Controller):

    def __init__(
        self,
        *args,
        bottles,
        dship,
        processing,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)
        self.view: RunFrame
        self.variables: MeasurementView = self.view.master  # pyright: ignore
        self.bottles = bottles
        self.dship = dship
        self.processing = processing
        self.batch_process = WindowsBatch()
        # set exe path in view
        self.view.path_to_seasave = self.configuration.path_to_seasave
        # define variables
        self.output_dir = self.configuration.output_directory
        self.last_filename = self.variables.last_filename
        self.current_filename: Path
        self.cast_number = self.variables.cast_number
        self.platform = self.variables.platform
        self.operator = self.variables.operator
        self.station = self.variables.station
        self.bottle_values = self.variables.bottle_frame.bottle_values
        # set callback methods
        self.view.add_callback("runseasave", self.run_seasave)
        self.view.add_callback("postruncheck", self.check_correct_filename)
        self.view.add_callback("runprocessing", self.run_processing)
        self.view.add_callback("cancelprocessing", self.cancel_processing)

    def run_seasave(
        self,
        file_name: str,
        downcast: bool = True,
        autostart: bool = False,
    ):
        self.update_variables_pre_run(autostart)
        self.current_filename = self.output_dir.joinpath(file_name)
        return RunSeasave(self.configuration, self.current_filename).run(
            downcast, autostart
        )

    def update_variables_post_run(self):
        self.configuration.last_platform = self.platform
        if self.current_filename.exists():
            self.last_filename.set(str(self.current_filename.name))
            self.configuration.last_cast = int(self.cast_number.get())
            self.cast_number.set(str(int(self.cast_number.get()) + 1))
            self.configuration.last_filename = Path(self.last_filename.get())
            self.configuration.operators["last"] = self.operator.get()
            self.configuration.write()

    def update_variables_pre_run(self, autostart):
        self.output_dir = self.configuration.output_directory
        self.bottles.data = {
            key: value.get() for key, value in self.bottle_values.items()
        }
        self.bottles.set_psa_bottle_info()
        MetadataHeader.build_metadata_header(
            configuration=self.configuration,
            dship_values=self.dship.dship_values,
            platform=self.platform,
            cast=self.cast_number.get(),
            operator=self.operator.get(),
            pos_alias=self.station.get(),
            autostart=autostart,
        )

    def check_correct_filename(self):
        self.update_variables_post_run()
        if str(self.current_filename).split("-")[0].endswith("000"):
            self.update_file_information()

    def update_file_information(self):
        station_and_event_info = self.dship.retrieve_station_and_event_info()
        if station_and_event_info:
            UpdateFiles(
                self.last_filename.get(),
                self.output_dir,
                station_and_event_info,
            )

    def run_processing(self, target_file: str):
        if not self.processing.file_path.suffix == ".toml":
            self.batch_process.run(self.processing.file_path, target_file)
        else:
            self.processing.input_file = target_file
            self.processing.run()
            self.configuration.last_processing_file = self.model.file_path
            self.configuration.write()

    def cancel_processing(self):
        if not self.processing.file_path.suffix == ".toml":
            self.batch_process.cancel()
        else:
            self.processing.cancel()
