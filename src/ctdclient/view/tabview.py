from typing import Type

import customtkinter as ctk
from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.view.configuration import ConfigurationView
from ctdclient.view.measurement import MeasurementView
from ctdclient.view.processing import ProcessingView


class TabView(ctk.CTkTabview):
    """Collection of multiple windows within one frame, reachable by tabs."""

    def __init__(
        self,
        window: ctk.CTkFrame,
        configuration: ConfigurationFile,
        tabs: dict[
            str, Type[MeasurementView | ProcessingView | ConfigurationView]
        ],
        *args,
        **kwargs,
    ):
        super().__init__(window, *args, **kwargs)

        for name, view in tabs.items():
            self.add(name)
            if name == "measurement":
                self.measurement = MeasurementView(
                    self.tab(name), configuration=configuration
                )
                self.measurement.grid()
            elif name == "processing":
                self.processing = ProcessingView(
                    self.tab(name), configuration=configuration
                )
                self.processing.grid()
            else:
                tab = view(master=self.tab(name), configuration=configuration)
                tab.grid()
