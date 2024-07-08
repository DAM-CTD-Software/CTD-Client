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
