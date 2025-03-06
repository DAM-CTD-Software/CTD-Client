import logging

import customtkinter as ctk
from ctdclient.controller.bottlecontroller import BottleController
from ctdclient.controller.configcontroller import ConfigurationController
from ctdclient.controller.dshipcontroller import DshipController
from ctdclient.controller.nrtcontroller import NRTController
from ctdclient.controller.processingcontroller import ProcessingController
from ctdclient.controller.runcontroller import RunController
from ctdclient.definitions import config
from ctdclient.model import BottleClosingDepths
from ctdclient.model.dshipcaller import DshipCaller
from ctdclient.model.near_real_time_publication import NRTList
from ctdclient.model.processing import ProcessingList
from ctdclient.view.configuration import AboutView
from ctdclient.view.configuration import ConfigurationView
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.mainwindow import MainWindow
from ctdclient.view.measurement import MeasurementView
from ctdclient.view.nrtcontrol import NRTControlFrame
from ctdclient.view.processing import ProcessingView

logger = logging.getLogger(__name__)


class MainController:
    def __init__(self, root_window: ctk.CTk):
        self.measurement = MeasurementView(root_window)
        self.config_view = ConfigurationView(root_window)
        self.processing_view = ProcessingView(root_window)
        self.nrt_control_view = NRTControlFrame(root_window)
        self.about_view = AboutView(root_window)

        self.mainwindow = MainWindow(
            parent=root_window,
            tab_dict=self.create_tabs(),
        )
        # processing
        self.processing = ProcessingList()
        self.processing_controller = ProcessingController(
            config,
            self.processing,
            self.processing_view,
        )
        # nrt
        self.nrt = NRTList()
        self.nrt_controller = NRTController(
            config, self.nrt, self.nrt_control_view
        )
        # config
        self.config_controller = ConfigurationController(
            config,
            config,
            self.config_view,
            measurementview=self.measurement,
        )
        # bottles
        self.bottles = BottleClosingDepths(config)
        self.bottle_view = self.measurement.bottle_frame
        self.bottle_controller = BottleController(
            config, self.bottles, self.bottle_view
        )
        # dship
        self.info_frame = self.measurement.info_frame
        self.dship = DshipCaller(config)
        self.dship_view = self.measurement.dship_frame
        self.dship_controller = DshipController(
            config,
            self.dship,
            self.dship_view,
            info_frame=self.info_frame,
        )
        # run Seasave
        self.run_view = self.measurement.run_frame
        self.run_controller = RunController(
            config,
            None,
            self.run_view,
            bottles=self.bottles,
            processing=self.processing,
        )

        self.mainwindow.grid(row=0, column=0, sticky="nsew")
        self.mainwindow.grid_rowconfigure(0, weight=1)
        self.mainwindow.grid_columnconfigure(0, weight=1)

    def create_tabs(self) -> dict[str, CtkFrame]:
        # TODO: implement config part to allow tab selection
        tab_dict = {
            "measurement": self.measurement,
            "processing": self.processing_view,
            "nrt publication": self.nrt_control_view,
            "config": self.config_view,
            "help": self.about_view,
        }
        return tab_dict

    def kill_threads(self):
        self.dship_controller.kill_threads()
        self.nrt.kill_processes()
