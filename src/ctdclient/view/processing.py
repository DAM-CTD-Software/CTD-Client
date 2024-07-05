from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import tkinter.font as tkFont
import customtkinter as ctk
from functools import partial
import difflib
from tomlkit.exceptions import NonExistentKey
from typing import Type

from ctdclient.view.View import ViewMixin
from ctdclient.configurationhandler import ConfigurationFile


class ProcessingView(ctk.CTkFrame, ViewMixin):
    """
    A frame to wrap all information and functionality for data processing.
    Is divided in two main parts, the configuration of input paths, to xmlcon,
    hex and psa folder, and the selection of processing modules and their
    respective psas.
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
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
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
        self.grid()

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
        frame = ctk.CTkFrame(self)
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
        self.grid()

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
        self.grid()

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
        frame = ctk.CTkFrame(self)
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
