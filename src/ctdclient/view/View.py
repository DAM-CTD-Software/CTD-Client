from pathlib import Path
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import tkinter.font as tkFont
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from functools import partial
import difflib
import datetime
from typing import Callable
import importlib.metadata
from sys import platform
from tomlkit.exceptions import NonExistentKey
import psutil

from ctdclient.fileupdater import UpdateFiles
from ctdclient.runseasave import RunSeasave


class MainWindow:
    """Top window that encapsulates all other frames."""

    def __init__(
        self, controller, root, config, dship_info, bottles, processing
    ):
        self.config = config
        root.title(
            f"DAM CTD Software v{
                importlib.metadata.version('ctdclient')}"
        )
        # Because CTkToplevel currently is bugged on windows
        # and doesn't check if a user specified icon is set
        # we need to set the icon again after 200ms
        if platform.startswith("win"):
            root.after(200, lambda: root.iconbitmap("icon.ico"))

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=14)
        root.option_add("*Font", default_font)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        root.geometry("620x780")

        root_frame = ctk.CTkFrame(root)
        root_frame.grid(row=0, column=0)

        # creating tab organisation
        tabs = TabView(
            root_frame,
            width=600,
            height=700,
            command=self.update_config_values,
        )
        tabs.grid()
        # building individual pages in their own classes
        self.measurement = Measurement(
            tabs.measurement,
            config,
            bottles,
            dship_info,
            controller,
            processing,
        )
        Processing(tabs.processing, config, processing)
        Configuration(tabs.configuration, config)
        tabs.measurement.grid()
        tabs.processing.grid()
        tabs.configuration.grid()

        root_frame.update_idletasks()

    def update_config_values(self):
        self.config.read_config(self.measurement.platform.get().lower())
        self.measurement.select_operator.configure(
            values=[
                item
                for item in list(self.config.operators.values())[:-1]
                if item != ""
            ]
        )


class TabView(ctk.CTkTabview):
    """Collection of multiple windows within one frame, reachable by tabs."""

    def __init__(self, window, **kwargs):
        super().__init__(window, **kwargs)

        self.add("measurement")
        self.add("processing")
        self.add("configuration")
        self.measurement = ctk.CTkFrame(self.tab("measurement"))
        self.processing = ctk.CTkFrame(self.tab("processing"))
        self.configuration = ctk.CTkFrame(self.tab("configuration"))


class Measurement:
    """
    A frame that displays the information needed for the CTD measurement,
    DSHIP live data, bottle closing depths and operator and allows to run
    the Seasave software with command line arguments.
    """

    def __init__(
        self, window, config, bottles, dship_info, controller, processing
    ):
        self.window = window
        self.config = config
        self.bottles = bottles
        self.dship_info = dship_info
        self.controller = controller
        self.processing = processing
        self.dship_values = dship_info.dship_values
        self.dship_vars = {
            key: tk.StringVar(value=value)
            for key, value in self.dship_values.items()
        }
        self.all_platforms = self.config.platforms
        self.save_btl_config = tk.BooleanVar(value=False)
        self.downcast_option = self.config.downcast_option

        # configure window layout
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=3)
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
            self.config.read_ctd_config("scanfish")
            self.frame_dship.grid(
                column=0, row=0, padx=self.padx, pady=self.pady
            )
            self.last_filename.set(self.config.last_filename.name)
            self.cast_number.set(self.config.last_cast + 1)

            self.frame_info.grid(
                column=0, row=1, padx=self.padx, pady=self.pady
            )
            self.frame_run.grid(
                column=0, row=2, columnspan=2, padx=self.padx, pady=self.pady
            )
            self.frame_stopwatch.grid_remove()
            self.frame_bottle.grid_remove()
        else:
            self.config.read_ctd_config(self.platform.get().lower())
            self.frame_dship.grid(
                column=0, row=0, padx=self.padx, pady=self.pady
            )
            self.last_filename.set(self.config.last_filename.name)
            self.cast_number.set(self.config.last_cast + 1)
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
        self.window.grid()

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
        dship_frame = ctk.CTkFrame(self.window)
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
        info_frame = ctk.CTkFrame(self.window)
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
        self.last_filename = tk.StringVar(value=self.config.last_filename.name)
        ctk.CTkLabel(info_frame, textvariable=self.last_filename).grid(
            row=1, column=1, sticky=tk.E
        )
        # operator selection
        ctk.CTkLabel(info_frame, text="Operator").grid(
            row=2, column=0, sticky=tk.W, padx=self.padx
        )
        self.operator = tk.StringVar(value=self.config.operators["last"])
        self.select_operator = ctk.CTkComboBox(
            info_frame,
            values=[
                item
                for item in list(self.config.operators.values())[:-1]
                if item != ""
            ],
            variable=self.operator,
        )
        self.select_operator.grid(row=2, column=1, sticky=tk.E)
        # cast selection/display
        ctk.CTkLabel(info_frame, text="Cast number").grid(
            row=3, column=0, sticky=tk.W, padx=self.padx
        )
        self.cast_number = tk.StringVar(value=self.config.last_cast + 1)
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
        self.platform.set(self.config.last_platform)
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
        bottle_frame = ctk.CTkFrame(self.window)
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
        self.window.grid()

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
        run_frame = ctk.CTkFrame(self.window)
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
        stopwatch_frame = ctk.CTkFrame(self.window)
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
        self.output_dir = self.config.output_directory
        full_file_path = self.output_dir.joinpath(self.current_filename.get())
        self.config.last_platform = self.platform.get()
        self.process = RunSeasave(self.config, full_file_path).run(
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
        self.config.reload()
        hex_file = tk.StringVar(value=self.config.last_filename)
        selected_file = self.select_file("hex", hex_file)
        if selected_file:
            try:
                self.processing.input_file = hex_file.get()
                self.processing.run()
            except TypeError:
                pass
            else:
                self.config.last_processing_file = self.processing.file_path
                self.config.write()

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


class Processing:
    """
    A frame to wrap all information and functionality for data processing.
    Is divided in two main parts, the configuration of input paths, to xmlcon,
    hex and psa folder, and the selection of processing modules and their
    respective psas.
    """

    def __init__(self, window, config, processing) -> None:
        self.window = window
        self.config = config
        self.processing = processing
        # TODO: extend these or handle differently
        self.psa_modules = [
            "alignctd",
            "airpressure",
            "binavg",
            "bottlesum",
            "celltm",
            "datcnv",
            "derive",
            "filter",
            "iow_btl_id",
            "loopedit",
            "wildedit",
            "w_filter",
        ]

        # layout
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)
        self.padx = 5
        self.pady = 5
        self.update_values()

    def update_values(self):
        self.psa_dir = tk.StringVar(
            value=self.processing.processing_info["psa_directory"]
        )
        try:
            self.psa_paths = [
                path.name for path in Path(self.psa_dir.get()).iterdir()
            ]
            self.psa_paths = sorted(self.psa_paths, key=str.lower)
        except FileNotFoundError as error:
            # TODO: open window with message
            pass

        self.steps = []
        self.path_dict = self.get_values_to_set()
        self.file_path = tk.StringVar(value=self.processing.file_path)

        if self.file_path.get().endswith(".toml"):
            self.path_frame = self.path_selection_frame()
        else:
            self.path_frame = self.custom_srcipt_frame()
        self.window.grid()

    def get_values_to_set(self):
        value_dict = {
            key: tk.StringVar(value=value)
            for key, value in self.processing.processing_info.items()
            if key not in ("modules", "file_list", "optional")
        }
        try:
            optional_values = {
                key: tk.StringVar(value=value)
                for key, value in self.processing.processing_info[
                    "optional"
                ].items()
            }
        except (NonExistentKey, KeyError):
            pass
        else:
            value_dict = {**value_dict, **optional_values}
        for value in value_dict.values():
            value.trace_add("write", self.update_processing_info)
        return value_dict

    def path_selection_frame(self):
        frame = ctk.CTkFrame(self.window)
        row = 0
        ctk.CTkLabel(
            frame,
            text="Processing settings",
            font=(tkFont.nametofont("TkDefaultFont"), 20),
        ).grid(
            row=row,
            column=0,
            sticky=tk.W,
            padx=self.padx,
            pady=self.pady,
        )
        ctk.CTkLabel(
            frame,
            text=Path(self.file_path.get()).name,
            font=(tkFont.nametofont("TkDefaultFont"), 14),
        ).grid(
            row=row,
            column=1,
            sticky=tk.E,
            padx=self.padx,
            pady=self.pady,
        )
        ttk.Separator(frame, orient="horizontal").grid(
            row=row + 1, sticky=tk.E + tk.W
        )
        for index, (name, variable) in enumerate(self.path_dict.items()):
            row = index + 2
            ctk.CTkLabel(frame, text=f"{name.replace('_', ' ')}: ").grid(
                row=row,
                column=0,
                sticky=tk.W,
                padx=self.padx,
                pady=self.pady,
            )
            if name in ("new_file_name", "file_suffix"):
                ctk.CTkEntry(frame, textvariable=variable).grid(
                    row=row,
                    column=1,
                    sticky=tk.E,
                    padx=self.padx,
                    pady=self.pady,
                )
            else:
                ctk.CTkLabel(
                    frame,
                    textvariable=variable,
                    font=(tkFont.nametofont("TkDefaultFont"), 10),
                ).grid(
                    row=row,
                    column=1,
                    sticky=tk.E,
                    padx=self.padx,
                    pady=self.pady,
                )
                command_with_arguments = partial(
                    self.select_file, name, variable
                )
                ctk.CTkButton(
                    frame,
                    text="Browse",
                    command=command_with_arguments,
                    width=28,
                ).grid(row=row, column=2, padx=self.padx, pady=self.pady)
            if name in self.processing.optional_options.keys():
                remove_option = partial(
                    self.remove_processing_option, name, variable
                )
                ctk.CTkButton(
                    frame,
                    text="-",
                    command=remove_option,
                    width=10,
                    height=10,
                ).grid(row=row, column=3)
        row += 1
        ctk.CTkLabel(frame, text="Add option:").grid(column=0, sticky=tk.W)
        self.option_variable = tk.StringVar(value="")
        new_option = ctk.CTkComboBox(
            frame,
            values=[
                str(key)
                for key in self.processing.optional_options.keys()
                if key not in self.path_dict.keys()
            ],
            variable=self.option_variable,
        )
        new_option.grid(
            row=row,
            column=1,
            sticky=tk.E,
            padx=self.padx,
            pady=self.pady,
        )
        add_processing_option = partial(self.add_processing_option)
        ctk.CTkButton(
            frame, text="+", width=10, height=10, command=add_processing_option
        ).grid(row=row, column=3, sticky=tk.E)
        frame.grid()
        self.step_selection_frame(frame, row + 1)
        self.config_save_load_frame(frame)
        return frame

    def add_processing_option(self):
        try:
            self.processing.processing_info["optional"][
                self.option_variable.get()
            ] = ""
        except KeyError:
            self.processing.processing_info["optional"] = {}
            self.processing.processing_info["optional"][
                self.option_variable.get()
            ] = ""
        self.path_frame.grid_forget()
        self.path_frame.destroy()
        self.update_values()

    def remove_processing_option(self, name, variable):
        del self.processing.processing_info[name]
        self.path_frame.grid_forget()
        self.path_frame.destroy()
        self.update_values()

    def step_selection_frame(self, frame, row):
        """
        Frame to hold the dynamic drop-downs for processing step and psa
        selection.
        """
        ctk.CTkLabel(
            frame,
            text="Processing steps",
            font=(tkFont.nametofont("TkDefaultFont"), 20),
        ).grid(
            row=row,
            column=0,
            sticky=tk.W,
            padx=self.padx,
            pady=self.pady,
        )
        ttk.Separator(frame, orient="horizontal").grid(
            row=row + 1, sticky=tk.E + tk.W
        )
        self.step_number = 1
        self.step_var_dict = {}
        # steps and psas frame
        modules_frame = ctk.CTkFrame(frame)
        for user_defined_step, psa_dict in self.processing.modules.items():
            if len(psa_dict) > 0:
                psa_value = psa_dict["psa"]
            else:
                psa_value = None
            self.add_processing_step(
                modules_frame, self.step_number, user_defined_step, psa_value
            )
        modules_frame.grid(column=1)
        frame.grid()
        return frame

    def config_save_load_frame(self, frame):
        row = len(frame.winfo_children())
        ctk.CTkButton(
            frame,
            text="Save current configuration",
            command=self.save_current_configuration,
        ).grid(row=row, column=0, sticky=tk.W, pady=10)
        ctk.CTkButton(
            frame, text="Load configuration", command=self.load_configuration
        ).grid(row=row, column=1, sticky=tk.E, pady=10)
        frame.grid()
        return frame

    def update_psa_selection(self, directory):
        """"""
        self.psa_paths = [path.name for path in Path(directory).iterdir()]
        self.psa_paths = sorted(self.psa_paths, key=str.lower)
        self.path_frame.grid_forget()
        self.path_frame.destroy()
        self.path_frame = self.path_selection_frame()
        self.window.grid()

    def add_processing_step(
        self, window, step_number=0, preset_value="", psa_value=None
    ):
        """
        Handles the processing step selection procedure.
        Automatically selects the closest named psa inside of the psa folder.

        Parameters
        ----------
        window : Parent frame

        preset_value : sets the name of the processing step, if already known
             (Default value = '')

        Returns
        -------

        """
        new_step = ctk.CTkFrame(window)
        step = tk.StringVar(value=preset_value)
        step.trace_add("write", self.update_processing_info)

        def psa_default_value(step_value):
            """
            Scans the psa folder for the closest string compared to the step.
            """
            try:
                psa_default_value = difflib.get_close_matches(
                    f"{step_value}.psa", self.psa_paths, n=1, cutoff=0.5
                )[0]
            except IndexError:
                psa_default_value = ""
            return psa_default_value

        def update_psa_value(comboboxObject):
            """Automatically updates the corresponding psa value upon selecting
            a processing step."""
            frame = new_step
            psa_box_object = frame.winfo_children()[1]
            psa_box_object.set(psa_default_value(comboboxObject))

        if not psa_value:
            psa_value = psa_default_value(preset_value)
        psa = tk.StringVar(value=psa_value)
        psa.trace_add("write", self.update_processing_info)
        self.step_var_dict[self.step_number] = (step, psa)

        step_box = ctk.CTkComboBox(
            new_step,
            values=self.psa_modules,
            variable=step,
            command=update_psa_value,
        )
        step_box.set(preset_value)
        step_box.grid(row=0, column=0, padx=2, pady=2)
        psa_box = ctk.CTkComboBox(
            new_step, values=self.psa_paths, variable=psa
        )
        psa_box.grid(row=0, column=1, padx=2, pady=2)
        # TODO: handle recursive case correctly to allow new step below current
        add_step = partial(self.new_processing_step, window, self.step_number)
        ctk.CTkButton(
            new_step, width=20, height=20, text="+", command=add_step
        ).grid(row=0, column=2)
        remove_step = partial(
            self.remove_processing_step, new_step, step_number
        )
        ctk.CTkButton(
            new_step, width=20, height=20, text="-", command=remove_step
        ).grid(row=0, column=3)
        new_step.grid()
        self.step_number += 1

    def new_processing_step(self, frame, step_number):
        self.add_processing_step(frame, step_number)

    def remove_processing_step(self, frame, step_number):
        """
        Handles all the steps needed to remove a processing step from the
        selection frame without leaving any code artifacts behind.
        """
        frame.grid_forget()
        frame.destroy()
        self.step_var_dict.pop(step_number)
        self.window.grid()

    def select_file(self, file_type: str, variable: tk.StringVar):
        """
        Generic file selection method, that opens a file browsing pop-up.
        """
        path = Path(variable.get())
        filetypes = (
            (f"{file_type} files", f"*.{file_type}"),
            ("All files", "*.*"),
        )

        if file_type in ("psas", "xmlcons") or file_type.endswith("directory"):
            directory = fd.askdirectory(
                title=f"Path to {file_type}",
                initialdir=path,
            )
            variable.set(directory)
            if file_type == "psa_directory":
                self.update_psa_selection(directory)

        else:
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

    def update_processing_info(self, *args, **kwargs):
        processing_dict = {
            key: value.get() for key, value in self.path_dict.items()
        }
        processing_dict = {
            **processing_dict,
            "modules": self.export_module_and_psa_info(),
        }
        self.processing.processing_info = processing_dict

    def export_module_and_psa_info(self) -> dict:
        try:
            info_dict = {
                key.get(): ({"psa": value.get()} if value.get() != "" else {})
                for _, (key, value) in self.step_var_dict.items()
            }
        except AttributeError:
            info_dict = {}
        return info_dict

    def save_current_configuration(self):
        current_file = Path(self.file_path.get())
        new_file_name = fd.asksaveasfilename(
            title="Save new config as",
            initialdir=current_file.parent,
            initialfile=current_file.name,
            defaultextension=".toml",
            filetypes=[
                ("toml file", ".toml"),
                ("batch script", ".bat"),
                ("All files", ".*"),
            ],
        )
        if new_file_name:
            self.file_path.set(new_file_name)
            processing_dict = {
                key: value.get()
                for key, value in self.path_dict.items()
                if key not in self.processing.optional_options.keys()
            }
            optional_dict = {
                key: value.get()
                for key, value in self.path_dict.items()
                if key in self.processing.optional_options.keys()
            }
            processing_dict = {
                **processing_dict,
                "optional": optional_dict,
                "modules": self.export_module_and_psa_info(),
            }
            self.processing.file_path = new_file_name
            self.processing.save(processing_dict)
            self.path_frame.grid_forget()
            self.path_frame.destroy()
            self.update_values()

    def load_configuration(self):
        if self.select_file("toml", self.file_path):
            path_to_file = Path(self.file_path.get())
            if path_to_file.suffix == ".toml":
                if self.processing.load(path_to_file=path_to_file):
                    self.processing.use_custom_script = False
                    self.path_frame.grid_forget()
                    self.path_frame.destroy()
                    self.update_values()
                else:
                    # TODO: open a message window
                    pass
            # allow custom scripts
            else:
                self.processing.use_custom_script = path_to_file
                self.path_frame.grid_forget()
                self.path_frame.destroy()
                self.file_path.set(str(path_to_file))
                self.path_frame = self.custom_srcipt_frame()

    def custom_srcipt_frame(self):
        frame = ctk.CTkFrame(self.window)
        ctk.CTkLabel(
            frame,
            text="Processing settings",
            font=(tkFont.nametofont("TkDefaultFont"), 20),
        ).grid(
            row=0,
            column=0,
            sticky=tk.W,
            padx=self.padx,
            pady=self.pady,
        )
        ttk.Separator(frame, orient="horizontal").grid(
            row=1, sticky=tk.E + tk.W
        )
        ctk.CTkLabel(
            frame,
            text=f"Custom script:     {Path(self.file_path.get()).name}",
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
            padx=self.padx,
            pady=self.pady,
        )
        ctk.CTkButton(
            frame, text="Load configuration", command=self.load_configuration
        ).grid(row=3, column=0, columnspan=3, pady=10)
        frame.grid()
        return frame


class Configuration:
    """ """

    def __init__(self, window, config) -> None:
        self.window = window
        self.config = config
        self.values_to_set = self.get_values_to_set()
        self.padx = 5
        self.pady = 5
        setting_frame = self.setting_frame()
        setting_frame.grid()
        self.window.grid()

    def get_values_to_set(self):
        value_dict = {}
        for instrument in self.config.platforms:
            value_dict.update(
                {
                    instrument: {
                        key: tk.StringVar(value=value)
                        for key, value in self.config[instrument.lower()][
                            "paths"
                        ].items()
                    }
                }
            )
        value_dict.update(
            {
                "operators": {
                    key: tk.StringVar(value=value)
                    for key, value in self.config.operators.items()
                }
            }
        )
        return value_dict

    def setting_frame(self):
        frame = ctk.CTkFrame(self.window)
        for index, (instrument, inner_dict) in enumerate(
            self.values_to_set.items()
        ):
            index *= len(inner_dict) + 2
            ctk.CTkLabel(
                frame,
                text=f"{instrument}",
                font=(tkFont.nametofont("TkDefaultFont"), 20),
            ).grid(
                row=index,
                column=0,
                sticky=tk.W,
                padx=self.padx,
                pady=self.pady,
            )
            ttk.Separator(frame, orient="horizontal").grid(
                row=index + 1, sticky=tk.E + tk.W
            )
            for inner_index, (name, variable) in enumerate(inner_dict.items()):
                row = index + inner_index + 2
                ctk.CTkLabel(frame, text=f"{name.replace('_', ' ')}: ").grid(
                    row=row,
                    column=0,
                    sticky=tk.W,
                    padx=self.padx,
                    pady=self.pady,
                )
                if instrument == "operators":
                    ctk.CTkEntry(frame, textvariable=variable).grid(
                        row=row,
                        column=1,
                        sticky=tk.E,
                        padx=self.padx,
                        pady=self.pady,
                    )
                else:
                    ctk.CTkLabel(
                        frame,
                        textvariable=variable,
                        font=(tkFont.nametofont("TkDefaultFont"), 10),
                    ).grid(
                        row=row,
                        column=1,
                        sticky=tk.E,
                        padx=self.padx,
                        pady=self.pady,
                    )
                    command_with_arguments = partial(
                        self.select_file, instrument, name, variable
                    )
                    ctk.CTkButton(
                        frame,
                        text="Browse",
                        command=command_with_arguments,
                        width=28,
                    ).grid(row=row, column=2, padx=self.padx, pady=self.pady)
        ctk.CTkButton(
            frame, text="Set operators", command=self.write_config, width=600
        ).grid(row=row, column=0, columnspan=3, padx=self.padx, pady=self.pady)
        return frame

    def write_config(self):
        self.config["operators"] = {
            key: value.get()
            for key, value in self.values_to_set["operators"].items()
        }
        self.config.write(use_internal_values=False)

    def select_file(self, instrument, name, variable):
        """
        Generic file selection method, that opens a file browsing pop-up.
        """
        if not name.endswith("directory"):
            if name.endswith("psa"):
                file_type = "psa"
            elif name.startswith("batch"):
                file_type = "bat"
            else:
                file_type = name
            path = Path(variable.get())
            filetypes = (
                (f"{file_type} files", f"*.{file_type}"),
                ("All files", "*.*"),
            )

            file = fd.askopenfilename(
                title=f"Path to {name}",
                initialdir=path.parent,
                initialfile=path.name,
                filetypes=filetypes,
            )
        else:
            file = fd.askdirectory(
                title=f"{name}",
                initialdir=variable.get(),
            )
        if file:
            variable.set(file)
            self.config[instrument.lower()]["paths"][name] = file
            self.config.write(use_internal_values=False)


class CTkSpinbox(ctk.CTkFrame):
    def __init__(
        self,
        *args,
        variable: tk.StringVar,
        width: int = 100,
        height: int = 32,
        step_size: int | float = 1,
        command: Callable | None = None,
        **kwargs,
    ):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.step_size = step_size
        self.command = command

        self.configure(fg_color=("gray78", "gray28"))  # set frame color

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.subtract_button = ctk.CTkButton(
            self,
            text="-",
            width=height - 6,
            height=height - 6,
            command=self.subtract_button_callback,
        )
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = ctk.CTkEntry(
            self,
            textvariable=variable,
            width=width - (2 * height),
            height=height - 6,
            border_width=0,
        )
        self.entry.grid(
            row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew"
        )

        self.add_button = ctk.CTkButton(
            self,
            text="+",
            width=height - 6,
            height=height - 6,
            command=self.add_button_callback,
        )
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = int(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = int(self.entry.get()) - self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def get(self) -> float | None:
        try:
            return float(self.entry.get())
        except ValueError:
            return None

    def set(self, value: float):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(float(value)))
        self.entry.insert(0, str(float(value)))
