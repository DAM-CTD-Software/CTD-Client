import tkinter as tk
import tkinter.font as tkFont
from pathlib import Path
from tkinter import ttk

import customtkinter as ctk
from ctdclient.utils import select_file
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.View import ViewMixin


class ProcessingCustomScriptFrame(ViewMixin, CtkFrame):

    def __init__(
        self,
        *args,
        file_path,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.file_path = file_path
        self.psa_paths = []
        self.step_options = []

        ctk.CTkLabel(
            self,
            text="Processing settings",
            font=(tkFont.nametofont("TkDefaultFont"), 20),
        ).grid(
            row=0,
            column=0,
            sticky=tk.W,
            padx=self.padx,
            pady=self.pady,
        )
        ttk.Separator(self, orient="horizontal").grid(
            row=1, sticky=tk.E + tk.W
        )
        ctk.CTkLabel(
            self,
            text=f"Custom script:     {Path(self.file_path).name}",
        ).grid(
            row=2,
            column=0,
            sticky=tk.W,
            padx=self.padx,
            pady=self.pady,
        )
        ctk.CTkButton(
            self, text="Load configuration", command=self.load_configuration
        ).grid(row=3, column=0, columnspan=3, pady=10)
        self.grid()

    def load_configuration(self):
        # TODO: change seletc_file to return the file name?
        file_path = tk.StringVar(value=str(self.file_path))
        file_selected = select_file("toml", file_path)
        if file_selected:
            self.callbacks["configload"](file_path.get())
