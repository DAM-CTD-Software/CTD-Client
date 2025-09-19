import sys
import tkinter.font as tkFont

import customtkinter as ctk
import psutil
from ctdclient.controller.maincontroller import MainController
from ctdclient.definitions import config
from ctdclient.definitions import ICON_PATH
from ctdclient.definitions import THEMES_PATH
from ctdclient.definitions import VERSION
from ctdclient.definitions import WRONG_CONFIG
from ctdclient.logconfig import LoggingConfig
from CTkMessagebox import CTkMessagebox


def main():
    """The main entry point of the software."""
    # if check_if_running():
    #     sys.exit("CTD-Client is already running.")
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
    """Checks, whether CTD-Client is already running"""
    current_process_name = "ctdclient"
    current_process_name += ".exe" if sys.platform.startswith("win") else ""
    for process in psutil.process_iter():
        try:
            # skip the process if its this one (using the process' creation
            # time here, as this software is multithreaded and spans three
            # processes upon starting, so PID would not be enough.)
            if process.create_time() != psutil.Process().create_time():
                if current_process_name == process.name():
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return False


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
