import customtkinter as ctk
from typing import Type

from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.view.configuration import ConfigurationView
from ctdclient.view.measurement import MeasurementView
from ctdclient.view.processing import ProcessingView


class TabView(ctk.CTkTabview):
    """Collection of multiple windows within one frame, reachable by tabs."""

    def __init__(
        self,
        window: ctk.CTkFrame,
        config: ConfigurationFile,
        tabs: dict[
            str, Type[MeasurementView | ProcessingView | ConfigurationView]
        ],
        *args,
        **kwargs,
    ):
        super().__init__(window, *args, **kwargs)

        for name, view in tabs.items():
            self.add(name)
            tab = view(parent=self.tab(name), configuration=config)
            tab.grid()

        # self.add("measurement")
        # self.add("processing")
        # self.add("configuration")
        # self.measurement = ctk.CTkFrame(self.tab("measurement"))
        # self.processing = ctk.CTkFrame(self.tab("processing"))
        # self.configuration = ctk.CTkFrame(self.tab("configuration"))
