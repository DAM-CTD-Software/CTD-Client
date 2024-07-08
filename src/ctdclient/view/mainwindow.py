from typing import Type

import customtkinter as ctk
from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.view.tabview import TabView


class MainWindow(ctk.CTkFrame):

    def __init__(
        self,
        parent: ctk.CTk,
        config: ConfigurationFile,
        tab_dict: dict[str, Type[ctk.CTkFrame]],
    ):
        super().__init__(parent)

        self.tabs = TabView(
            window=self,
            configuration=config,
            tabs=tab_dict,
            width=600,
            height=700,
            # command=self.update_config_values,
        )
        self.tabs.grid()
