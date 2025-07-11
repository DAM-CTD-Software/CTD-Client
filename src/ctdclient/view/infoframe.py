import tkinter as tk
from multiprocessing import Queue

import customtkinter as ctk
from ctdclient.model.metadataheader import MetadataHeader
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
        self.set_border()
        for arg in args:
            if arg.__class__.__name__ == "MeasurementView":
                self.platform = arg.platform
                self.last_filename = arg.last_filename
                self.cast_number = arg.cast_number
                self.current_filename = arg.current_filename
                self.operator = arg.operator
                self.station = arg.station

    def initialize(self):
        if len(self.winfo_children()) > 0:
            for child in self.winfo_children():
                child.grid_forget()
                child.destroy()

        ctk.CTkLabel(self, text="Current filename").grid(
            row=0, column=0, sticky=tk.W, padx=self.padx
        )
        ctk.CTkLabel(self, textvariable=self.current_filename).grid(
            row=0, column=1, sticky=tk.E
        )
        # last filename
        ctk.CTkLabel(self, text="Last filename").grid(
            row=1, column=0, sticky=tk.W, padx=self.padx
        )
        ctk.CTkLabel(self, textvariable=self.last_filename).grid(
            row=1, column=1, sticky=tk.E
        )
        # cast selection/display
        ctk.CTkLabel(self, text="Cast number").grid(
            row=2, column=0, sticky=tk.W, padx=self.padx
        )
        CTkSpinbox(self, variable=self.cast_number).grid(
            row=2, column=1, sticky=tk.E
        )
        # operator selection
        ctk.CTkLabel(self, text="Operator").grid(
            row=3, column=0, sticky=tk.W, padx=self.padx
        )
        ctk.CTkComboBox(
            self,
            values=[
                item
                for item in list(self.configuration["operators"].values())[:-1]
                if item != ""
            ],
            variable=self.operator,
        ).grid(row=3, column=1, sticky=tk.E)
        # scanfish-specific option to override the current Pos_Alias
        ctk.CTkLabel(self, text="Override Position Alias").grid(
            row=5, column=0, sticky=tk.W, padx=self.padx
        )
        ctk.CTkEntry(
            self,
            textvariable=self.station,
        ).grid(row=5, column=1, sticky=tk.E)
        self.grid()

    def update_filename(self, queue: Queue):
        try:
            while not queue.empty():
                data = queue.get()
                self.current_filename.set(
                    MetadataHeader.build_file_name(
                        data,
                        int(self.cast_number.get()),
                        self.platform,
                    )
                )
        except Exception:
            pass
        self.after(1000, self.update_filename, queue)
