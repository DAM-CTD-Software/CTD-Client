import tkinter as tk

from ctdclient.view.bottleframe import BottleFrame
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.dshipframe import DshipFrame
from ctdclient.view.infoframe import InfoFrame
from ctdclient.view.runframe import RunFrame
from ctdclient.view.stopwatchframe import StopwatchFrame
from ctdclient.view.View import ViewMixin


class MeasurementView(CtkFrame, ViewMixin):
    """
    A frame that displays the information needed for the CTD measurement,
    DSHIP live data, bottle closing depths and operator and allows to run
    the Seasave software with command line arguments.
    """

    def __init__(
        self,
        *args,
        platform: str = "CTD",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = "measurement"

        # setting variables according to configuration file
        # TODO: add option to set the platform
        self.platform = platform
        self.downcast_option = self.configuration.downcast_option
        self.last_filename = tk.StringVar(
            value=self.configuration.last_filename.name
        )
        self.cast_number = tk.StringVar(
            value=str(self.configuration.last_cast + 1)
        )
        self.current_filename = tk.StringVar(value="")
        self.operator = tk.StringVar(
            value=self.configuration.operators["last"]
        )
        self.station = tk.StringVar(value="")

        # configure window layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)

        # children frames set-up
        self.bottle_frame = BottleFrame(self, configuration=self.configuration)
        self.dship_frame = DshipFrame(self, configuration=self.configuration)
        self.info_frame = InfoFrame(self, configuration=self.configuration)
        self.stopwatch_frame = StopwatchFrame(
            self, configuration=self.configuration
        )
        self.run_frame = RunFrame(self, configuration=self.configuration)

        # TODO: where to put this?
        self.configuration.read_ctd_config(self.platform.lower())

        # positioning of individual frames
        self.dship_frame.grid(column=0, row=0, padx=self.padx, pady=self.pady)
        self.info_frame.grid(column=0, row=1, padx=self.padx, pady=self.pady)
        self.run_frame.grid(
            column=0, row=3, columnspan=2, padx=self.padx, pady=self.pady
        )
        self.stopwatch_frame.grid(
            column=0, row=2, columnspan=2, padx=self.padx, pady=self.pady
        )
        self.bottle_frame.grid(
            column=1, row=0, rowspan=2, padx=self.padx, pady=self.pady
        )
        self.grid()
