# setting for pyinstaller to allow clean stopage of all threads
import multiprocessing
multiprocessing.freeze_support()
from pathlib import Path
import platform
import sys
import customtkinter as ctk
from code_tools.repeating import RepeatedTimer
from code_tools.logging import configure_logging

from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.dshipcaller import DSHIPHeader
from ctdclient.bottles import BottleClosingDepths
from ctdclient.view import MainWindow


configure_logging("ctdclient.log")


class Controller:
    """
    Controller in the spirit of the MVC model.
    Executes the business logic behind this GUI. At the moment, this is mostly
    just bringing together the individual bits, as well as listening to the
    dship class and updating the view accordingly.
    """

    def __init__(self):
        self.root = ctk.CTk()
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
            sys.exit(1)
        self.config = ConfigurationFile(config_path)
        self.dship_info = DSHIPHeader(self.config, dummy=True)
        self.bottles = BottleClosingDepths(self.config)
        self.main_window = MainWindow(
            self, self.root, self.config, self.dship_info, self.bottles
        )
        # fullscreen option:
        # root.after(0, lambda: root.state('zoomed'))
        self.start_listener()
        self.root.mainloop()
        self.end_listener()
        self.dship_info.end_listener()

    def start_listener(self):
        """
        Activates the listener to periodically check for new dship values.
        """
        self.listener = RepeatedTimer(
            self.config.dhsip_fetch_intervall,
            self.update_dship_values,
        )

    def end_listener(self):
        """
        Ends the listener, will mostly be called when closing the program.
        """
        self.listener.stop()

    def update_dship_values(self):
        """Transfers the dship values to the main window."""
        self.main_window.measurement.update_dship_values(
            self.dship_info.dship_values.values()
        )
        if self.dship_info.fail_counter == self.dship_info.fail_tolerance:
            self.end_listener()
            self.main_window.measurement.set_dship_status_bad()
        else:
            self.main_window.measurement.set_dship_status_good()
        self.main_window.measurement.update_file_name(
            self.dship_info.build_file_name(
                self.main_window.measurement.cast_number,
                self.main_window.measurement.platform.get(),
            )
        )

    def reconnect_dship(self):
        self.dship_info.start_listener()
        if self.dship_info.last_call == "successful":
            self.update_dship_values()
            # self.main_window.measurement.set_dship_status_good()
        self.start_listener()


if __name__ == "__main__":
    controller = Controller()
