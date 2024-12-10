from code_tools.logging import get_logger
from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.controller.bottlecontroller import BottleController
from ctdclient.controller.configcontroller import ConfigurationController
from ctdclient.controller.dshipcontroller import DshipController
from ctdclient.controller.processingcontroller import ProcessingController
from ctdclient.controller.runcontroller import RunController
from ctdclient.definitions import ROOT_PATH
from ctdclient.eventmanager import EventManager
from ctdclient.model import BottleClosingDepths
from ctdclient.model.dshipcaller import DshipCaller
from ctdclient.model.near_real_time_publication import DailyPublication
from ctdclient.model.near_real_time_publication import (
    instantiate_near_real_time_target,
)
from ctdclient.model.near_real_time_publication import NearRealTimeTarget
from ctdclient.model.processing import Processing
from ctdclient.view.mainwindow import MainWindow
from tomlkit.toml_file import TOMLFile

logger = get_logger(__name__)


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
        event_manager = EventManager()

        # processing
        self.processing = Processing(configuration, event_manager)
        self.near_real_time_publications = []
        for path in ROOT_PATH.glob("nrt_*.toml"):
            try:
                self.near_real_time_publications.append(
                    instantiate_near_real_time_target(
                        **TOMLFile(path).read(), event_manager=event_manager
                    )
                )
            except Exception as error:
                logger.error(
                    f"Could not instantiate nrt, using {
                        path}: {error}"
                )
                continue

        # bottles
        self.bottles = BottleClosingDepths(configuration)
        self.bottle_view = self.measurement.bottle_frame
        self.bottle_controller = BottleController(
            configuration, self.bottles, self.bottle_view
        )

        # dship
        self.info_frame = self.measurement.info_frame
        self.dship = DshipCaller(configuration)
        self.dship_view = self.measurement.dship_frame
        self.dship_controller = DshipController(
            configuration,
            self.dship,
            self.dship_view,
            info_frame=self.info_frame,
        )

        # run Seasave
        self.run_view = self.measurement.run_frame
        self.run_controller = RunController(
            configuration,
            None,
            self.run_view,
            bottles=self.bottles,
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

    def kill_threads(self):
        self.dship_controller.kill_threads()
        for item in self.near_real_time_publications:
            if isinstance(item, DailyPublication):
                item.stop()
