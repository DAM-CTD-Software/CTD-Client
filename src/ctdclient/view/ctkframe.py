import customtkinter as ctk
from ctdclient.configurationhandler import ConfigurationFile


class CtkFrame(ctk.CTkFrame):

    def __init__(
        self,
        *args,
        configuration: ConfigurationFile,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.configuration = configuration
        self.padx = 5
        self.pady = 5
        self.configure(fg_color="transparent")

    def set_border(self, width: int = 1, color: str = "gray10"):
        """Sets a uniform, minimal border around the frame."""
        self.configure(border_width=width, border_color=color)
