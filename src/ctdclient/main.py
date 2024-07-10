import importlib.metadata
import sys
import tkinter.font as tkFont
from typing import Type

import customtkinter as ctk
from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.controller.maincontroller import MainController
from ctdclient.definitions import CONFIG_PATH
from ctdclient.definitions import THEMES_PATH
from ctdclient.view.configuration import ConfigurationView
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.mainwindow import MainWindow
from ctdclient.view.measurement import MeasurementView


def main():
    configuration_file = ConfigurationFile(CONFIG_PATH)
    root = ctk.CTk()
    root.title(
        f"DAM CTD Software v{
            importlib.metadata.version('ctdclient')}"
    )
    # Because CTkToplevel currently is bugged on windows
    # and doesn't check if a user specified icon is set
    # we need to set the icon again after 200ms
    if sys.platform.startswith("win"):
        root.after(200, lambda: root.iconbitmap("icon.ico"))

    default_font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(size=14)
    root.option_add("*Font", default_font)
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme(THEMES_PATH)
    root.geometry("620x780")
    main_window = MainWindow(
        parent=root,
        config=configuration_file,
        tab_dict=create_tabs(configuration_file),
    )
    MainController(configuration_file, main_window)
    main_window.grid(row=0, column=0)
    root.mainloop()


def create_tabs(config: ConfigurationFile) -> dict[str, Type[CtkFrame]]:
    # TODO: implement config part to allow tab selection
    tab_dict = {
        "measurement": MeasurementView,
        # "processing": ProcessingView,
        "configuration": ConfigurationView,
    }
    return tab_dict


if __name__ == "__main__":
    main()
