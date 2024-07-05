from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog as fd
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import datetime
import psutil

from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.fileupdater import UpdateFiles
from ctdclient.model.runseasave import RunSeasave
from ctdclient.view.View import ViewMixin
from ctdclient.view.ctkspinbox import CTkSpinbox


class MeasurementView(ctk.CTkFrame, ViewMixin):
    """
    A frame that displays the information needed for the CTD measurement,
    DSHIP live data, bottle closing depths and operator and allows to run
    the Seasave software with command line arguments.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        configuration: ConfigurationFile,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self.configuration = configuration
        self.bottles = bottles
        self.dship_info = dship_info
        self.controller = controller
        self.processing = processing
        self.dship_values = dship_info.dship_values
        self.dship_vars = {
            key: tk.StringVar(value=value)
            for key, value in self.dship_values.items()
        }
        self.all_platforms = self.configuration.platforms
        self.save_btl_config = tk.BooleanVar(value=False)
        self.downcast_option = self.configuration.downcast_option

        # configure window layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.padx = 5
        self.pady = 5

        # frame set-up
        self.frame_dship = self.dship_frame()
        self.frame_info = self.info_frame()
        self.frame_bottle = self.bottle_frame()
        self.frame_stopwatch = self.stopwatch_frame()
        self.frame_run = self.run_frame()

        self.update_frames()

    def update_frames(self, *args):
        self.bottles.instantiate_bottle_info()
        if self.platform.get() == "Scanfish":
            self.configuration.read_ctd_config("scanfish")
            self.frame_dship.grid(
                column=0, row=0, padx=self.padx, pady=self.pady
            )
            self.last_filename.set(self.configuration.last_filename.name)
            self.cast_number.set(self.configuration.last_cast + 1)

            self.frame_info.grid(
                column=0, row=1, padx=self.padx, pady=self.pady
            )
            self.frame_run.grid(
                column=0, row=2, columnspan=2, padx=self.padx, pady=self.pady
            )
            self.frame_stopwatch.grid_remove()
            self.frame_bottle.grid_remove()
        else:
            self.configuration.read_ctd_config(self.platform.get().lower())
            self.frame_dship.grid(
                column=0, row=0, padx=self.padx, pady=self.pady
            )
            self.last_filename.set(self.configuration.last_filename.name)
            self.cast_number.set(self.configuration.last_cast + 1)
            self.frame_info.grid(
                column=0, row=1, padx=self.padx, pady=self.pady
            )
            self.frame_run.grid(
                column=0, row=3, columnspan=2, padx=self.padx, pady=self.pady
            )
            self.frame_stopwatch.grid(
                column=0, row=2, columnspan=2, padx=self.padx, pady=self.pady
            )
            self.frame_bottle.grid(
                column=1, row=0, rowspan=2, padx=self.padx, pady=self.pady
            )
        self.grid()

    def update_dship_values(self, list_of_values):
        """

        Parameters
        ----------
        list_of_values :


        Returns
        -------

        """
        for (_, var), value in zip(self.dship_vars.items(), list_of_values):
            var.set(value)

    def dship_frame(self):
        """
        Frame that displays our metadata header information with live-fetched
        DSHIP data. Additionally features a selection field for the current
        operators name, as this is the only header information that can not be
        retrieved from DSHIP.

        Parameters
        ----------
        window :


        Returns
        -------

        """
        # show live dhsip values
        dship_frame = ctk.CTkFrame(self)
        self.dship_label = ctk.CTkLabel(
            dship_frame, text="waiting for connection..."
        )
        self.dship_label.grid(row=0, column=0)
        ctk.CTkButton(
            dship_frame, text="Reconnect", command=self.reconnect_dship
        ).grid(row=0, column=1)

        for index, (key, value) in enumerate(self.dship_vars.items()):
            if key != "Cruise":
                ctk.CTkLabel(dship_frame, text=key).grid(
                    row=index + 1, column=0
                )
                ctk.CTkLabel(dship_frame, textvariable=value).grid(
                    row=index + 1, column=1
                )

        return dship_frame

    def info_frame(self):
        """
        Frame that displays the filename, that is currently created, and allows
        cast number and operator name selection.
        """
        info_frame = ctk.CTkFrame(self)
        # current filename
        self.current_filename = tk.StringVar(value="")
        ctk.CTkLabel(info_frame, text="current filename").grid(
            row=0, column=0, sticky=tk.W, padx=self.padx
        )
        ctk.CTkLabel(info_frame, textvariable=self.current_filename).grid(
            row=0, column=1, sticky=tk.E
        )
        # last filename
        ctk.CTkLabel(info_frame, text="last filename").grid(
            row=1, column=0, sticky=tk.W, padx=self.padx
        )
        self.last_filename = tk.StringVar(
            value=self.configuration.last_filename.name
        )
        ctk.CTkLabel(info_frame, textvariable=self.last_filename).grid(
            row=1, column=1, sticky=tk.E
        )
        # operator selection
        ctk.CTkLabel(info_frame, text="Operator").grid(
            row=2, column=0, sticky=tk.W, padx=self.padx
        )
        self.operator = tk.StringVar(
            value=self.configuration.operators["last"]
        )
        self.select_operator = ctk.CTkComboBox(
            info_frame,
            values=[
                item
                for item in list(self.configuration.operators.values())[:-1]
                if item != ""
            ],
            variable=self.operator,
        )
        self.select_operator.grid(row=2, column=1, sticky=tk.E)
        # cast selection/display
        ctk.CTkLabel(info_frame, text="Cast number").grid(
            row=3, column=0, sticky=tk.W, padx=self.padx
        )
        self.cast_number = tk.StringVar(value=self.configuration.last_cast + 1)
        CTkSpinbox(info_frame, variable=self.cast_number).grid(
            row=3, column=1, sticky=tk.E
        )
        # platform selection
        ctk.CTkLabel(info_frame, text="Platform").grid(
            row=4, column=0, sticky=tk.W, padx=self.padx
        )
        # platform_selector = ctk.CTkComboBox(
        self.platform = ctk.CTkComboBox(
            info_frame,
            values=self.all_platforms,
            # variable=self.platform,
            command=self.update_frames,
        )
        self.platform.set(self.configuration.last_platform)
        # platform_selector.grid(row=4, column=1, sticky=tk.E)
        self.platform.grid(row=4, column=1, sticky=tk.E)
        # scanfish-specific option to override the current Pos_Alias
        self.station = tk.StringVar(value="")
        ctk.CTkLabel(info_frame, text="Override Pos_Alias").grid(
            row=5, column=0, sticky=tk.W, padx=self.padx
        )
        ctk.CTkEntry(
            info_frame,
            textvariable=self.station,
        ).grid(row=5, column=1, sticky=tk.E)

        return info_frame

    def bottle_frame(self):
        """
        Frame to allow setting the bottle closing depths.

        Parameters
        ----------
        window :


        Returns
        -------

        """
        # configure bottle closing times
        bottle_frame = ctk.CTkFrame(self)
        depth_frame = ctk.CTkScrollableFrame(bottle_frame, height=400)
        self.bottle_values = {}
        ctk.CTkLabel(depth_frame, text="BottleIDs").grid(column=0, row=0)
        ctk.CTkLabel(depth_frame, text="Depth to close").grid(row=0, column=1)
        for index, (key, value) in enumerate(self.bottles.items()):
            textvariable = tk.StringVar()
            textvariable.set(value)
            self.bottle_values[key] = textvariable
            ctk.CTkLabel(depth_frame, text=key).grid(row=index + 1, column=0)
            ctk.CTkEntry(
                depth_frame, textvariable=textvariable, justify="center"
            ).grid(row=index + 1, column=1)
        depth_frame.grid()
        ctk.CTkButton(
            bottle_frame, text="Reset bottles", command=self.reset_bottles
        ).grid(row=2, column=0, columnspan=2, pady=5)
        return bottle_frame

    def reset_bottles(self):
        for variable in self.bottle_values.values():
            variable.set("")
        self.frame_bottle.grid()
        self.grid()

    def run_frame(self):
        """
        Frame that wraps the seasave.exe start button with two checkboxes for
        the command line options.

        Parameters
        ----------
        window :


        Returns
        -------

        """
        # start measurement
        run_frame = ctk.CTkFrame(self)
        self.autostart = tk.BooleanVar(value=True)
        self.downcast = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            run_frame,
            text="autostart",
            variable=self.autostart,
        ).grid(row=0, pady=2)
        row = 1
        if self.downcast_option:
            ctk.CTkCheckBox(
                run_frame,
                text="downcast",
                variable=self.downcast,
            ).grid(row=row)
            row += 1
        ctk.CTkButton(
            run_frame,
            text="Start Seasave",
            command=self.start_seasave,
        ).grid(row=row, column=0, sticky=tk.W, padx=20, pady=5)
        self.processing_button = ctk.CTkButton(
            run_frame, text="Run Processing", command=self.processing_thread
        )
        self.processing_button.grid(
            row=row, column=1, sticky=tk.E, padx=20, pady=5
        )
        run_frame.grid()
        return run_frame

    def update_button(self):
        if self.proc_thread.is_alive():
            button_name = "Cancel"
            button_command = self.cancel_processing
            self.processing_button.after(1000, self.update_button)
        else:
            button_name = "Run Processing"
            button_command = self.processing_thread
        self.processing_button.configure(
            text=button_name, command=button_command
        )

    def processing_thread(self):
        self.proc_thread = threading.Thread(target=self.run_processing)
        self.proc_thread.start()
        self.update_button()

    def stopwatch_frame(self):
        """Frame that acts as a simple stopwatch."""
        stopwatch_frame = ctk.CTkFrame(self)
        self.timer_seconds = 0
        self.stopwatch_label = ctk.CTkLabel(
            stopwatch_frame,
            height=70,
            width=70,
            corner_radius=20,
            text="00:00:00",
            font=("Normal", 15, "bold"),
        )
        self.stopwatch_label.grid()

        def update():
            self.timer_seconds += 1
            self.stopwatch_label.configure(
                text=str(datetime.timedelta(seconds=self.timer_seconds))
            )
            self.stopwatch_label.after(1000, update)

        def reset(event):
            self.timer_seconds = 0

        self.stopwatch_label.bind("<Button-1>", reset)
        self.stopwatch_label.bind(
            "<Enter>",
            command=lambda e: self.stopwatch_label.configure(
                fg_color="#1e7898"
            ),
        )
        self.stopwatch_label.bind(
            "<Leave>",
            command=lambda e: self.stopwatch_label.configure(
                fg_color="transparent"
            ),
        )
        update()
        return stopwatch_frame

    def start_seasave(self):
        """
        Method that is called upon clicking 'Start Seasave'. Organizes
        the information flow of bottle closing information and dship metadata.
        """
        # TODO: handle exceptions
        # TODO: move into controller
        if self.process_exists("thunderbird"):
            CTkMessagebox(
                title="Warning",
                message="Seasave is already running!",
                icon="warning",
                option_1="Ok",
            )
            return
        if (self.current_filename.get() == self.last_filename.get()) and Path(
            self.last_filename.get()
        ).exists():
            msg = CTkMessagebox(
                title="Warning",
                message=f"Caution! Do you really want to override the last filename {
                    self.last_filename.get()}?",
                icon="warning",
                option_1="Cancel",
                option_2="Yes",
            )
            if msg.get() == "Cancel":
                return
        if self.platform.get() != "Scanfish":
            self.bottles.update_bottle_information(
                {key: value.get() for key, value in self.bottle_values.items()}
            )
        self.dship_info.build_metadata_header(
            self.platform.get(),
            self.cast_number.get(),
            self.operator.get(),
            pos_alias=self.station.get(),
        )

        self.last_filename.set(self.current_filename.get())
        self.cast_number.set(str(int(self.cast_number.get()) + 1))
        self.output_dir = self.configuration.output_directory
        full_file_path = self.output_dir.joinpath(self.current_filename.get())
        self.configuration.last_platform = self.platform.get()
        self.process = RunSeasave(self.configuration, full_file_path).run(
            self.downcast.get(), self.autostart.get()
        )
        self.check_seasave()

    def check_seasave(self):
        if self.process.poll() is not None:
            station_and_event_info = (
                self.dship_info.retrieve_station_and_event_info(
                    cruise_id=self.dship_vars["Cruise"].get()
                )
            )
            if station_and_event_info:
                UpdateFiles(
                    self.last_filename.get(),
                    self.output_dir,
                    station_and_event_info,
                )
        else:
            self.frame_run.after(1000, self.check_seasave)

    def process_exists(self, process_name: str) -> bool:
        progs = {p.info["name"].lower() for p in psutil.process_iter(["name"])}
        if process_name in progs:
            return True
        else:
            return False

    def run_processing(self):
        """Collects the processing step information and feeds it into the
        batch processing routine."""
        self.configuration.reload()
        hex_file = tk.StringVar(value=self.configuration.last_filename)
        selected_file = self.select_file("hex", hex_file)
        if selected_file:
            try:
                self.processing.input_file = hex_file.get()
                self.processing.run()
            except TypeError:
                pass
            else:
                self.configuration.last_processing_file = (
                    self.processing.file_path
                )
                self.configuration.write()

    def cancel_processing(self):
        self.processing.cancel()

    def select_file(self, file_type, variable):
        """
        Generic file selection method, that opens a file browsing pop-up.
        """
        path = Path(variable.get())
        filetypes = (
            (f"{file_type} files", f"*.{file_type}"),
            ("All files", "*.*"),
        )
        file = fd.askopenfilename(
            title=f"Path to {file_type}",
            initialdir=path.parent,
            initialfile=path.name,
            filetypes=filetypes,
        )
        if file:
            variable.set(file)
            return True
        else:
            return False

    def reconnect_dship(self):
        """"""
        self.controller.reconnect_dship()

    def set_dship_status_good(self):
        """"""
        self.dship_label.configure(text_color="green", text="DSHIP live")

    def set_dship_status_bad(self):
        """"""
        self.dship_label.configure(text_color="red", text="not connected")

    def update_file_name(self, name):
        """"""
        self.current_filename.set(name)
