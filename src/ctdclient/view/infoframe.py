import tkinter as tk

import customtkinter as ctk
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.ctkspinbox import CTkSpinbox
from ctdclient.view.View import ViewMixin


class InfoFrame(ViewMixin, CtkFrame):
    """
    Frame that displays the filename, that is currently created, and allows
    cast number and operator name selection.
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        for arg in args:
            if hasattr(arg, "name"):
                if arg.name == "measurement":
                    self.last_filename = arg.last_filename
                    self.cast_number = arg.cast_number
                    self.current_filename = arg.current_filename
                    self.operator = arg.operator
                    self.station = arg.station
                    self.initialize()

    def initialize(self):
        ctk.CTkLabel(self, text="current filename").grid(
            row=0, column=0, sticky=tk.W, padx=self.padx
        )
        ctk.CTkLabel(self, textvariable=self.current_filename).grid(
            row=0, column=1, sticky=tk.E
        )
        # last filename
        ctk.CTkLabel(self, text="last filename").grid(
            row=1, column=0, sticky=tk.W, padx=self.padx
        )
        ctk.CTkLabel(self, textvariable=self.last_filename).grid(
            row=1, column=1, sticky=tk.E
        )
        # operator selection
        ctk.CTkLabel(self, text="Operator").grid(
            row=2, column=0, sticky=tk.W, padx=self.padx
        )
        ctk.CTkComboBox(
            self,
            values=[
                item
                for item in list(self.configuration.operators.values())[:-1]
                if item != ""
            ],
            variable=self.operator,
        ).grid(row=2, column=1, sticky=tk.E)
        # cast selection/display
        ctk.CTkLabel(self, text="Cast number").grid(
            row=3, column=0, sticky=tk.W, padx=self.padx
        )
        CTkSpinbox(self, variable=self.cast_number).grid(
            row=3, column=1, sticky=tk.E
        )
        # platform selection
        ctk.CTkLabel(self, text="Platform").grid(
            row=4, column=0, sticky=tk.W, padx=self.padx
        )
        # scanfish-specific option to override the current Pos_Alias
        ctk.CTkLabel(self, text="Override Pos_Alias").grid(
            row=5, column=0, sticky=tk.W, padx=self.padx
        )
        ctk.CTkEntry(
            self,
            textvariable=self.station,
        ).grid(row=5, column=1, sticky=tk.E)
