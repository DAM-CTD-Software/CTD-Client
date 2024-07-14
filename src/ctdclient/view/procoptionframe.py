import tkinter as tk
import tkinter.font as tkFont
from functools import partial
from pathlib import Path
from tkinter import ttk

import customtkinter as ctk
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.procstepframe import ProcessingStepFrame
from ctdclient.view.View import ViewMixin


class ProcessingOptionFrame(ViewMixin, CtkFrame):

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        for arg in args:
            if arg.__class__.__name__ == "ProcessingView":
                self.file_path = arg.file_path
                self.path_dict = arg.path_dict
                self.initialize()

    def initialize(self):
        row = 0
        ctk.CTkLabel(
            self,
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
            self,
            text=Path(self.file_path.get()).name,
            font=(tkFont.nametofont("TkDefaultFont"), 14),
        ).grid(
            row=row,
            column=1,
            sticky=tk.E,
            padx=self.padx,
            pady=self.pady,
        )
        ttk.Separator(self, orient="horizontal").grid(
            row=row + 1, sticky=tk.E + tk.W
        )
        for index, (name, variable) in enumerate(self.path_dict.items()):
            row = index + 2
            ctk.CTkLabel(self, text=f"{name.replace('_', ' ')}: ").grid(
                row=row,
                column=0,
                sticky=tk.W,
                padx=self.padx,
                pady=self.pady,
            )
            if name in ("new_file_name", "file_suffix"):
                ctk.CTkEntry(self, textvariable=variable).grid(
                    row=row,
                    column=1,
                    sticky=tk.E,
                    padx=self.padx,
                    pady=self.pady,
                )
            else:
                ctk.CTkLabel(
                    self,
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
                    self.master.select_file, name, variable
                )
                ctk.CTkButton(
                    self,
                    text="Browse",
                    command=command_with_arguments,
                    width=28,
                ).grid(row=row, column=2, padx=self.padx, pady=self.pady)
            if name in self.processing.optional_options.keys():
                remove_option = partial(
                    self.remove_processing_option, name, variable
                )
                ctk.CTkButton(
                    self,
                    text="-",
                    command=remove_option,
                    width=10,
                    height=10,
                ).grid(row=row, column=3)
        row += 1
        ctk.CTkLabel(self, text="Add option:").grid(column=0, sticky=tk.W)
        self.option_variable = tk.StringVar(value="")
        new_option = ctk.CTkComboBox(
            self,
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
            self, text="+", width=10, height=10, command=add_processing_option
        ).grid(row=row, column=3, sticky=tk.E)
        self.grid()
        ProcessingStepFrame(self, row + 1)
        self.config_save_load_frame(self)

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
