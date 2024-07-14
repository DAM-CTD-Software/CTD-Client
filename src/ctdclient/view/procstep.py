import difflib
import tkinter as tk

import customtkinter as ctk
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.View import ViewMixin


class ProcessingStep(ViewMixin, CtkFrame):
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

    def __init__(
        self,
        *args,
        step: tk.StringVar,
        psa: tk.StringVar,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.step = step
        self.step.trace_add("write", self.set_closest_psa_value)
        self.psa = psa
        # is being set by controller
        self.psa_paths = self.master.psa_paths

        if self.psa.get() in ("", None):
            self.set_closest_psa_value()

        step_box = ctk.CTkComboBox(
            self,
            values=["datcnv", "derive"],
            variable=self.step,
        )
        step_box.grid(row=0, column=0, padx=2, pady=2)
        psa_box = ctk.CTkComboBox(
            self, values=self.psa_paths, variable=self.psa
        )
        psa_box.grid(row=0, column=1, padx=2, pady=2)
        ctk.CTkButton(
            self,
            width=20,
            height=20,
            text="+",
            command=self.new_processing_step,
        ).grid(row=0, column=2)
        ctk.CTkButton(
            self, width=20, height=20, text="-", command=self.remove_step
        ).grid(row=0, column=3)
        self.grid()

    def set_closest_psa_value(self, *args, **kwargs):
        """
        Scans the psa folder for the closest string compared to the step.
        """
        try:
            psa_value = difflib.get_close_matches(
                f"{self.step.get()}.psa", self.psa_paths, n=1, cutoff=0.5
            )[0]
        except IndexError:
            psa_value = ""
        self.psa.set(psa_value)

    def new_processing_step(self):
        self.master.add_step(self)

    def remove_step(self):
        self.master.remove_step(self)
