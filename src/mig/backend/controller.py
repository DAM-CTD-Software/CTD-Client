import platform
import sys
import customtkinter as ctk

from mig.backend.configurationhandler import ConfigurationFile
from mig.backend.dshipcaller import DSHIPHeader, RepeatedTimer
from mig.frontend.main import MainWindow


class Controller:
    """
    Controller in the spirit of the MVC model.
    Executes the business logic behind this GUI. At the moment, this is mostly
    just bringing together the individual bits, as well as listening to the
    dship class and updating the view accordingly.
    """

    def __init__(self):
        # root = tk.Tk()
        self.root = ctk.CTk()
        if platform.system() == 'Linux':
            config_path = 'master_config.toml'
        elif platform.system() == 'Windows':
            from pathlib import Path
            file_location = Path(__file__).parents[3]
            config_path = file_location.joinpath('windows_config.toml')
        else:
            sys.exit(1)
        self.config = ConfigurationFile(config_path)
        self.dship_info = DSHIPHeader(self.config)
        self.main_window = MainWindow(self.root, self.config, self.dship_info)
        # fullscreen option:
        # root.after(0, lambda: root.state('zoomed'))
        self.start_listener()
        self.root.mainloop()
        self.dship_info.end_listener()

    def start_listener(self):
        """
        Activates the listener to periodically check for new dship values.
        """
        self.listener = RepeatedTimer(5, self.update_dship_values)

    def end_listener(self):
        """
        Ends the listener, will mostly be called when closing the program.
        """
        self.listener.stop()

    def update_dship_values(self):
        """Transfers the dship values to the main window."""
        try:
            self.main_window.measurement.update_dship_values(
                self.dship_info.dict_of_samples.values())
            self.main_window.measurement.dship_label['background'] = 'green'
        except AssertionError:
            self.main_window.measurement.dship_label['background'] = 'red'
            if self.dship_info.dship_fail_counter > 9:
                self.end_listener()
                self.main_window.measurement.dship_label['text'] = 'No DSHIP connection'


if __name__ == "__main__":
    controller = Controller()
    controller.end_listener()
