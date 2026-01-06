import customtkinter as ctk

from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.tabview import TabView


class MainWindow(ctk.CTkFrame):
    def __init__(
        self,
        parent: ctk.CTk,
        tab_dict: dict[str, CtkFrame],
    ):
        super().__init__(parent)

        self.tabs = TabView(
            window=self,
            tabs=tab_dict,
        )
        self.tabs.grid(row=0, column=0, sticky="nsew")
        # self.tabs.grid_rowconfigure(0, weight=1)
        # self.tabs.grid_columnconfigure(0, weight=1)
