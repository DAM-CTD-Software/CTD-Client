import socket
import sys
import tkinter.font as tkFont

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from ctdclient.controller.maincontroller import MainController
from ctdclient.definitions import (
    ICON_PATH,
    THEMES_PATH,
    VERSION,
    WRONG_CONFIG,
    config,
)
from ctdclient.logconfig import LoggingConfig

# global variable to keep the socket lock alive
_lock_socket = None


def main():
    """The main entry point of the software."""
    if check_if_running():
        sys.exit("CTD-Client is already running.")
    # set ctk options
    root = ctk.CTk()
    root.title(f"DAM CTD Software {VERSION}")
    # Because CTkToplevel currently is bugged on windows
    # and doesn't check if a user specified icon is set
    # we need to set the icon again after 200ms
    if sys.platform.startswith("win"):
        root.after(200, lambda: root.iconbitmap(ICON_PATH))

    default_font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(size=14)
    root.option_add("*Font", default_font)
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme(str(THEMES_PATH))
    ctk.set_widget_scaling(config.scaling)
    root.geometry("700x780")
    # initialize objects
    main_controller = MainController(root)
    main_window = main_controller.mainwindow

    LoggingConfig(root=root, logger_name=__name__)

    if WRONG_CONFIG:
        main_window.after(2000, inform_about_bad_config, main_window)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.mainloop()
    # clean up for shutdown
    main_controller.kill_threads()


def check_if_running() -> bool:
    """Checks whether CTD-Client is already running using a socket lock"""
    global _lock_socket

    _lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        _lock_socket.bind(("127.0.0.1", 59432))
        return False
    except OSError:
        return True


def inform_about_bad_config(main_window):
    answer = CTkMessagebox(
        title="Old config file",
        message="Your configuration file seems to be outdated. A new one has been generated and is being used for this session. Please make sure that all the necessary settings are (still) correct.",
        icon="warning",
        option_1="Ok",
    )
    if answer.get() == "Ok":
        main_window.tabs.configuration.tabs.set("expert settings")
        main_window.tabs.set("configuration")
        CTkMessagebox(
            title="Caution",
            message="These settings can break the application, proceed with caution and only if you know what you are doing.",
            option_1="Ok",
        )


if __name__ == "__main__":
    # necessary for PyInstaller, to avoid spawning endless loops of the Clients
    # process. See https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html
    import multiprocessing

    multiprocessing.freeze_support()

    main()

    sys.exit(0)
