from pathlib import Path
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
from processing.processing import Processing as own_processing

from ctdclient.batchprocessing import BatchProcessing, WindowsBatch
from ctdclient.runseasave import RunSeasave


class MainWindow:
    """Top window that encapsulates all other frames."""

    def __init__(self, controller, root, config, dship_info, bottles):
        self.config = config
        root.title("DAM CTD Software")
        # avoids old 'tear-off' menus
        root.option_add("*tearOff", tk.FALSE)

        root.geometry("700x800")
        root.resizable(width=0, height=0)

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=14)
        root.option_add("*Font", default_font)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # initialize standard menu
        # MenuBar(root)

        # creating tab organisation
        # select one out of NoteBookView, TabView and LabelFrames
        tabs = TabView(root, command=self.update_config_values)
        tabs.grid()
        # building individual pages in their own classes
        self.measurement = Measurement(
            tabs.measurement, config, bottles, dship_info, controller
        )
        Processing(tabs.processing, config)
        Configuration(tabs.configuration, config)
        tabs.measurement.grid()
        tabs.processing.grid()
        tabs.configuration.grid()

    def update_config_values(self):
        self.config.read_config(self.measurement.platform.get().lower())
        self.measurement.select_operator.configure(
            values=[
                item
                for item in list(self.config.operators.values())[:-1]
                if item != ""
            ]
        )


class NoteBookView(ttk.Notebook):
    """Basic tkinter equivalent to ctk's TabView."""

    def __init__(self, window):
        super().__init__(window)

        self.measurement = ctk.CTkFrame(self)
        self.processing = ctk.CTkFrame(self)
        self.configuration = ctk.CTkFrame(self)
        self.add(self.measurement, text="measurement")
        self.add(self.processing, text="processing")
        self.add(self.configuration, text="configuration")


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


class LabelFrames(ttk.PanedWindow):
    """
    Displaying multiple windows next to each other, separated inside boxes.
    """

    def __init__(self, window, **kwargs):
        super().__init__(window, orient=tk.HORIZONTAL, **kwargs)
        self.measurement = ctk.CTkFrame(self, text="measurement")
        self.processing = ctk.CTkFrame(self, text="processing")
        self.configuration = ctk.CTkFrame(self, text="configuration")
        self.add(self.measurement)
        self.add(self.processing)
        self.add(self.configuration)


class MenuBar:
    """Menu bar that allows some basic configuration."""

    def __init__(self, window) -> None:
        # TODO: implement
        menubar = tk.Menu(window)
        window["menu"] = menubar
        menu_file = tk.Menu(menubar)
        menu_edit = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label="File")
        menubar.add_cascade(menu=menu_edit, label="Edit")


class Measurement:
    """
    A frame that displays the information needed for the CTD measurement,
    DSHIP live data, bottle closing depths and operator and allows to run
    the Seasave software with command line arguments.
    """

    def __init__(self, window, config, bottles, dship_info, controller):
        self.window = window
        self.config = config
        self.bottles = bottles
        self.dship_info = dship_info
        self.controller = controller
        self.dship_values = dship_info.dship_values
        self.dship_vars = {
            key: tk.StringVar(value=value)
            for key, value in self.dship_values.items()
        }
        self.all_platforms = self.config.platforms
        self.save_btl_config = tk.BooleanVar(value=False)

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
            row=0, column=0, sticky=tk.W
        )
        ctk.CTkLabel(info_frame, textvariable=self.current_filename).grid(
            row=0, column=1, sticky=tk.E
        )
        # last filename
        ctk.CTkLabel(info_frame, text="last filename").grid(
            row=1, column=0, sticky=tk.W
        )
        self.last_filename = tk.StringVar(value=self.config.last_filename.name)
        ctk.CTkLabel(info_frame, textvariable=self.last_filename).grid(
            row=1, column=1, sticky=tk.E
        )
        # operator selection
        ctk.CTkLabel(info_frame, text="Operator").grid(
            row=2, column=0, sticky=tk.W
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
            row=3, column=0, sticky=tk.W
        )
        self.cast_number = tk.StringVar(value=self.config.last_cast + 1)
        CTkSpinbox(info_frame, variable=self.cast_number).grid(
            row=3, column=1, sticky=tk.E
        )
        # platform selection
        ctk.CTkLabel(info_frame, text="Platform").grid(
            row=4, column=0, sticky=tk.W
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
        ctk.CTkLabel(info_frame, text="Station").grid(
            row=5, column=0, sticky=tk.W
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
        self.bottle_values = {}
        ctk.CTkLabel(bottle_frame, text="BottleIDs").grid(column=0, row=0)
        ctk.CTkLabel(bottle_frame, text="Depth to close").grid(row=0, column=1)
        for index, (key, value) in enumerate(self.bottles.items()):
            textvariable = tk.StringVar()
            textvariable.set(value)
            self.bottle_values[key] = textvariable
            ctk.CTkLabel(bottle_frame, text=key).grid(row=index + 1, column=0)
            ctk.CTkEntry(
                bottle_frame, textvariable=textvariable, justify="center"
            ).grid(row=index + 1, column=1)
        # ctk.CTkCheckBox(
        #     bottle_frame,
        #     text="Save Bottle Configuration",
        #     variable=self.save_btl_config,
        # ).grid(column=1)
        return bottle_frame

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
        ctk.CTkCheckBox(
            run_frame,
            text="autostart",
            variable=self.autostart,
        ).grid()
        # self.downcast = tk.BooleanVar(value=True)
        # ctk.CTkCheckBox(
        #     run_frame,
        #     text="downcast",
        #     variable=self.downcast,
        # ).grid()
        ctk.CTkButton(
            run_frame,
            text="Start Seasave",
            command=self.start_seasave,
        ).grid()
        return run_frame

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
        if self.current_filename.get() == self.last_filename.get():
            msg = CTkMessagebox(
                title="Warning",
                message=f"Caution! Do you really want to override the last filename {self.last_filename.get()}?",
                icon="warning",
                option_1="Cancel",
                option_2="Go on",
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
            )
        else:
            self.dship_info.build_metadata_header(
                self.platform.get(),
                self.cast_number.get(),
                self.operator.get(),
                pos_alias=self.station.get(),
                autostart=self.autostart.get(),
            )

        self.last_filename.set(self.current_filename.get())
        self.cast_number.set(str(int(self.cast_number.get()) + 1))
        output_dir = self.config.output_directory
        full_file_path = output_dir.joinpath(self.current_filename.get())
        self.config.last_platform = self.platform.get()
        RunSeasave(self.config, full_file_path).run(self.autostart.get())

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

    def __init__(self, window, config) -> None:
        self.window = window
        self.psa_modules = [
            "AlignCTD",
            "AirPressure",
            "BinAvg",
            "BottleSum",
            "CellTM",
            "DatCnv",
            "Derive",
            "Filter",
            "LoopEdit",
            "WildEdit",
            "W_Filter",
        ]
        self.config = config
        self.path_dict = {
            "xmlcon": tk.StringVar(value=config.xmlcon),
            "hex": tk.StringVar(value=config.last_filename),
            "psas": tk.StringVar(value=config.psa_directory),
        }
        self.psa_paths = [
            path.name for path in self.config.psa_directory.iterdir()
        ]
        self.steps = []
        self.processing_type = "windowsbatch"

        # layout
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)
        self.padx = 5
        self.pady = 5

        if self.processing_type != "windowsbatch":
            self.step_frame = self.step_selection_frame()
            self.path_frame = self.path_selection_frame()
        self.run_processing_frame()
        self.window.grid()

    def path_selection_frame(self, padx=5, pady=5):
        """
        Frame that encapsulates the selection of the three paths needed in
        order to run the processing.
        """
        frame = tk.Frame(self.window)
        for index, (file_type, variable) in enumerate(self.path_dict.items()):
            # individual frame construction
            single_frame = tk.Frame(frame)
            single_frame.columnconfigure(0, weight=1)
            single_frame.columnconfigure(1, weight=7)
            single_frame.columnconfigure(2, weight=1)
            ctk.CTkLabel(single_frame, text=f"Path to {file_type}").grid(
                row=index, column=0, sticky=tk.W, padx=padx, pady=pady
            )
            tk.Entry(single_frame, textvariable=variable).grid(
                row=index, column=1, sticky=tk.E, padx=padx, pady=pady
            )
            command_with_arguments = partial(
                self.select_file, file_type, variable
            )
            ctk.CTkButton(
                single_frame, text="Browse", command=command_with_arguments
            ).grid(row=index, column=2, padx=padx, pady=pady)
            single_frame.grid()
        frame.grid()
        return frame

    def step_selection_frame(self):
        """
        Frame to hold the dynamic drop-downs for processing step and psa
        selection.
        """
        frame = tk.Frame(self.window)
        self.step_number = 1
        self.step_var_dict = {}
        # steps and psas frame
        modules_frame = tk.Frame(frame)
        for user_defined_step in self.steps:
            self.add_processing_step(modules_frame, user_defined_step)
        modules_frame.grid()
        # button frame
        button_frame = tk.Frame(frame)
        add_step = partial(self.add_processing_step, modules_frame)
        ctk.CTkButton(
            button_frame, text="Add processing step", command=add_step
        ).grid(row=0, column=0)
        remove_step = partial(self.remove_processing_step, modules_frame)
        # remove step button
        ctk.CTkButton(
            button_frame, text="Remove processing step", command=remove_step
        ).grid(row=0, column=1)
        button_frame.grid()
        frame.grid()
        return frame

    def run_processing_frame(self):
        frame = tk.Frame(self.window)
        # run processing button
        ctk.CTkButton(
            frame, text="Run processing", command=self.run_processing
        ).grid()
        frame.grid(column=0, columnspan=2, padx=self.padx, pady=self.pady)
        return frame

    def update_psa_selection(self, directory):
        """"""
        self.psa_paths = [path.name for path in Path(directory).iterdir()]
        self.step_frame.grid_forget()
        self.step_frame.destroy()
        self.step_frame = self.step_selection_frame()
        self.window.grid()

    def add_processing_step(self, window, preset_value=""):
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
        new_step = tk.Frame(window)
        step = tk.StringVar(value=preset_value)

        def psa_default_value(step_value):
            """
            Scans the psa folder for the closest string compared to the step.
            """
            try:
                psa_default_value = difflib.get_close_matches(
                    step_value, self.psa_paths, n=1
                )[0]
            except IndexError:
                psa_default_value = ""
            return psa_default_value

        def update_psa_value(comboboxObject):
            """Automatically updates the corresponding psa value upon selecting
            a processing step."""
            frame = comboboxObject.widget.master
            psa_box_object = frame.winfo_children()[-1]
            psa_box_object.set(psa_default_value(comboboxObject.widget.get()))

        psa = tk.StringVar(value=psa_default_value(preset_value))
        self.step_var_dict[self.step_number] = (step, psa)

        step_box = ctk.CTkComboBox(
            new_step, values=self.psa_modules, textvariable=step
        )
        step_box.set(preset_value)
        step_box.grid(row=0, column=0)
        step_box.bind("<<ComboboxSelected>>", update_psa_value)
        psa_box = ctk.CTkComboBox(
            new_step, values=self.psa_paths, textvariable=psa
        )
        psa_box.grid(row=0, column=1)
        new_step.grid()
        self.step_number += 1

    def remove_processing_step(self, frame):
        """
        Handles all the steps needed to remove a processing step from the
        selection frame without leaving any code artifacts behind.
        """
        last_element = frame.winfo_children()[-1]
        last_element.grid_forget()
        last_element.destroy()
        self.step_var_dict.pop(self.step_number - 1)
        self.step_number -= 1

    def run_processing(self):
        """Collects the processing step information and feeds it into the
        batch processing routine."""
        try:
            info_dict = {
                key.get(): value.get()
                for _, (key, value) in self.step_var_dict.items()
            }
        except AttributeError:
            pass
        if self.processing_type == "canadian":
            batch_processing = BatchProcessing(self.config, info_dict)
            batch_processing.run()
        elif self.processing_type == "own":
            proc = own_processing(
                config_path=self.config.path_to_config,
                steps=info_dict,
                input_file=self.config.last_filename,
            )
            proc.run()
        elif self.processing_type == "windowsbatch":
            self.config.reload()
            self.path_dict["hex"] = tk.StringVar(
                value=self.config.last_filename
            )
            selected_file = self.select_file("hex", self.path_dict["hex"])
            if selected_file:
                try:
                    WindowsBatch(
                        self.config.path_to_batch,
                        self.path_dict["hex"].get(),
                    )
                except TypeError:
                    pass

    def select_file(self, file_type, variable):
        """
        Generic file selection method, that opens a file browsing pop-up.
        """
        path = Path(variable.get())
        filetypes = (
            (f"{file_type} files", f"*.{file_type}"),
            ("All files", "*.*"),
        )

        if file_type == "psas":
            directory = fd.askdirectory(
                title=f"Path to {file_type}",
                initialdir=path,
            )
            variable.set(directory)
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


class Configuration:
    """ """

    def __init__(self, window, config) -> None:
        self.window = window
        self.config = config
        # self.values_to_set = {
        #     "output directory": tk.StringVar(
        #         value=self.config.output_directory
        #     ),
        #     "xmlcon": tk.StringVar(value=self.config.xmlcon),
        #     "Seasave Psa": tk.StringVar(value=self.config.seasave_psa),
        #     "vCTD-Batch": tk.StringVar(value=self.config.path_to_batch),
        #     "psa directory": tk.StringVar(value=self.config.psa_directory),
        # }
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
            elif name.endswith("batch"):
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
