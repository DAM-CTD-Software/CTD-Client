import tkinter as tk

import customtkinter as ctk

from ctdclient.model.bottles import BottleClosingDepths
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.View import ViewMixin


class BottleFrame(ViewMixin, CtkFrame):
    """
    Frame to allow setting the bottle closing depths.

    Parameters
    ----------
    window :


    Returns
    -------

    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    def initialize(self, bottles: BottleClosingDepths):
        self.bottles = bottles
        depth_frame = ctk.CTkScrollableFrame(self, height=400)
        depth_frame.configure(
            border_width=1, border_color="gray10", fg_color="transparent"
        )
        self.bottle_values = {}
        ctk.CTkLabel(depth_frame, text="BottleIDs").grid(column=0, row=0)
        ctk.CTkLabel(depth_frame, text="Depth to close").grid(row=0, column=1)
        for index, (key, value) in enumerate(self.bottles.items()):
            textvariable = tk.StringVar()
            textvariable.set(value)
            self.bottle_values[key] = textvariable
            ctk.CTkLabel(depth_frame, text=str(key)).grid(
                row=index + 1, column=0
            )
            ctk.CTkEntry(
                depth_frame, textvariable=textvariable, justify="center"
            ).grid(row=index + 1, column=1)
        depth_frame.grid()
        ctk.CTkButton(
            self, text="Reset bottles", command=self.reset_bottles
        ).grid(row=2, column=0, columnspan=2, pady=5)

    def reset_bottles(self):
        for variable in self.bottle_values.values():
            variable.set("")
        self.grid()
