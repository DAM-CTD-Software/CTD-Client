import customtkinter as ctk
from ctdclient.definitions import config


class CtkFrame(ctk.CTkFrame):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.configuration = config
        self.padx = 5
        self.pady = 5
        self.configure(fg_color="transparent")

    def set_border(self, width: int = 1, color: str = "gray10"):
        """Sets a uniform, minimal border around the frame."""
        self.configure(border_width=width, border_color=color)

    def kill(self):
        self.grid_forget()
        self.destroy()
