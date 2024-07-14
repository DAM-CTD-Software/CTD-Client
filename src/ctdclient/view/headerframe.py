import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk

import customtkinter as ctk
from ctdclient.view.ctkframe import CtkFrame


class HeaderFrame(CtkFrame):

    def __init__(
        self,
        *args,
        header_text: str,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        ctk.CTkLabel(
            self,
            text=header_text,
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
