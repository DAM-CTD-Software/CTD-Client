from typing import Type

import customtkinter as ctk
from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.measurement import MeasurementView
from ctdclient.view.processing import ProcessingView
from CTkMessagebox import CTkMessagebox


class TabView(ctk.CTkTabview):
    """Collection of multiple windows within one frame, reachable by tabs."""

    def __init__(
        self,
        window: ctk.CTkFrame,
        configuration: ConfigurationFile,
        tabs: dict[str, Type[CtkFrame]],
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
            elif name == "configuration":
                self.configuration = view(
                    self.tab(name), configuration=configuration
                )
                self.configuration.grid()
            elif name == "basic settings":
                self.basic_settings = view(
                    self.tab(name), configuration=configuration
                )
                self.basic_settings.grid()
            else:
                tab = view(master=self.tab(name), configuration=configuration)
                tab.grid()
        self.configure(command=self.on_tab_change)

    def on_tab_change(self):
        if self.get() == "expert settings":
            CTkMessagebox(
                title="Caution",
                message="These settings can break the application, proceed with caution and only if you know what you are doing.",
                option_1="Ok",
            )
