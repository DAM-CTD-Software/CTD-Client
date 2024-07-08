import importlib.metadata
import platform
import sys
import tkinter.font as tkFont
from pathlib import Path
from typing import Type

import customtkinter as ctk
from code_tools.logging import configure_logging
from code_tools.logging import get_logger
from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.controller.Controller import Controller
from ctdclient.controller.maincontroller import MainController
from ctdclient.view.configuration import ConfigurationView
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.mainwindow import MainWindow
from ctdclient.view.measurement import MeasurementView

configure_logging("ctdclient.log")
logger = get_logger(__name__)


def main():
    if platform.system() == "Linux":
        config_path = "linux_config.toml"
    elif platform.system() == "Windows":
        # check position of config_file
        file_location = Path(__file__).parents[1]
        config_path = file_location.joinpath("ctdclient.toml")
        if not config_path.is_file():
            file_location = Path(__file__).parents[3]
            config_path = file_location.joinpath("ctdclient.toml")
    else:
        logger.error("No configuration file found. Aborting.")
        sys.exit(1)
    configuration_file = ConfigurationFile(config_path)
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
    ctk.set_default_color_theme("dark-blue")
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
