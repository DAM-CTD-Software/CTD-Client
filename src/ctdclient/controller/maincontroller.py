from ctdclient.definitions import DSHIP
from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.controller.bottlecontroller import BottleController
from ctdclient.controller.configcontroller import ConfigurationController
from ctdclient.controller.dshipcontroller import DshipController
from ctdclient.controller.processingcontroller import ProcessingController
from ctdclient.controller.runcontroller import RunController
from ctdclient.model import BottleClosingDepths
from ctdclient.model.dshipcaller import DshipCaller
from ctdclient.model.processing import Processing
from ctdclient.view.mainwindow import MainWindow


class MainController:

    def __init__(
        self,
        configuration: ConfigurationFile,
        mainwindow: MainWindow,
    ):

        self.configuration = configuration
        self.mainwindow = mainwindow
        self.tabs = mainwindow.tabs
        self.measurement = self.tabs.measurement
        self.configuration_view = self.tabs.configuration

        self.processing = Processing()
        self.processing.file_path = configuration.last_processing_file
        # bottles
        self.bottles = BottleClosingDepths(configuration)
        self.bottle_view = self.measurement.bottle_frame
        self.bottle_controller = BottleController(
            configuration, self.bottles, self.bottle_view
        )

        # dship
        self.dship = DshipCaller(configuration, dummy=not DSHIP)
        self.dship_view = self.measurement.dship_frame
        self.dship_controller = DshipController(
            configuration, self.dship, self.dship_view
        )

        # run Seasave
        self.run_view = self.measurement.run_frame
        self.run_controller = RunController(
            configuration,
            None,
            self.run_view,
            bottles=self.bottles,
            dship=self.dship,
            processing=self.processing,
        )

        # processing
        try:
            self.processing_view = self.tabs.processing
        except AttributeError:
            pass
        else:
            self.processing_controller = ProcessingController(
                configuration,
                self.processing,
                self.processing_view,
            )

        # configuration
        self.config_controller = ConfigurationController(
            configuration,
            configuration,
            self.configuration_view,
            measurementview=self.measurement,
        )

        # check for update upon start
        # self.check_updates()

    def check_updates(self):
        # TODO: think about check intervall during run time
        self.mainwindow.check_for_update()
