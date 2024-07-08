from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.controller.bottlecontroller import BottleController
from ctdclient.controller.dshipcontroller import DshipController
from ctdclient.controller.runcontroller import RunController
from ctdclient.model import BottleClosingDepths
from ctdclient.model.dshipcaller import DshipCaller
from ctdclient.view.mainwindow import MainWindow


class MainController:

    def __init__(
        self,
        configuration: ConfigurationFile,
        mainwindow: MainWindow,
    ):

        self.configuration = configuration
        self.tabs = mainwindow.tabs
        self.measurement = self.tabs.measurement

        # bottles
        self.bottles = BottleClosingDepths(configuration)
        self.bottle_view = self.measurement.bottle_frame
        self.bottle_controller = BottleController(
            configuration, self.bottles, self.bottle_view
        )

        # dship
        self.dship = DshipCaller(configuration)
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
        )

        # processing
        # self.processing = MyProcessing()
