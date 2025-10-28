from ctdclient.controller.Controller import Controller
from ctdclient.model.plotting import Plotting
from ctdclient.view.plotting import PlottingFrame


class PlottingController(Controller):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.model: Plotting
        self.view: PlottingFrame
        self.view.add_callback("plot_file", self.plot_file)
        self.view.add_callback("plot_cruise", self.plot_cruise)
        self.view.add_callback("update_auto_plot", self.update_auto_plot)
        self.view.add_callback("open_config", self.open_config)

    def plot_file(self, file: str):
        self.model.plot_file(file)

    def plot_cruise(self, directory: str):
        self.model.plot_cruise(directory)

    def update_auto_plot(self, auto_plot: str):
        self.model.toggle_auto_plot(bool(auto_plot))

    def open_config(self):
        self.model.open_config()
