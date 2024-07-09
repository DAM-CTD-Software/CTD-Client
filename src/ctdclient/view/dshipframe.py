import tkinter as tk

import customtkinter as ctk
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.View import ViewMixin


class DshipFrame(ViewMixin, CtkFrame):
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

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.set_border()
        self.dship_values: dict

    def initialize(self, dship_values: dict):
        self.dship_values = dship_values
        self.dship_vars = {
            key: tk.StringVar(value=value)
            for key, value in self.dship_values.items()
        }
        self.dship_label = ctk.CTkLabel(self, text="waiting for connection...")
        self.dship_label.grid(row=0, column=0)
        ctk.CTkButton(
            self,
            text="Reconnect",
            command=self.bind_commands_to_callbacks("reconnect"),
        ).grid(row=0, column=1)

        for index, (key, value) in enumerate(self.dship_vars.items()):
            if key != "Cruise":
                ctk.CTkLabel(self, text=key).grid(row=index + 1, column=0)
                ctk.CTkLabel(self, textvariable=value).grid(
                    row=index + 1, column=1
                )

    def update_dship_values(self, dship_answer: dict):
        """

        Parameters
        ----------
        list_of_values :


        Returns
        -------

        """
        for (_, var), value in zip(
            self.dship_vars.items(), dship_answer.values()
        ):
            var.set(value)

    def set_dship_status_good(self):
        """"""
        self.dship_label.configure(text_color="green", text="DSHIP live")

    def set_dship_status_bad(self):
        """"""
        self.dship_label.configure(text_color="red", text="not connected")
