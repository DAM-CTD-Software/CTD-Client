import customtkinter as ctk
from ctdclient.model.near_real_time_publication import NearRealTimeTarget
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.nrtconfig import NRTConfigurator


class NRTControlFrame(CtkFrame):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

    def instantiate(self, nrt_list: list):
        # clean slate before refilling the frame
        for frame in self.winfo_children():
            frame.destroy()
            frame.grid_forget()
        for nrt in nrt_list:
            self.create_nrt_overview(nrt)

    def create_nrt_overview(self, nrt: NearRealTimeTarget):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(
            row=0, column=0, sticky="ew", padx=self.padx, pady=self.pady
        )

        name = ctk.CTkLabel(frame, text=nrt.name)
        name.grid(row=0, column=0, padx=self.padx, pady=self.pady)

        status = ctk.CTkLabel(
            frame,
            text=str(nrt.active),
            text_color="green" if nrt.active else "red",
        )
        status.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        config = ctk.CTkButton(
            frame, text="open config", command=self.open_config(nrt)
        )
        config.grid(row=1, column=0, padx=self.padx, pady=self.pady)

    def open_config(self, nrt: NearRealTimeTarget):
        config_window = ctk.CTkToplevel(
            self, title=f"Config for {nrt.file_path}"
        )

        editor = NRTConfigurator(
            config_window,
            config_file=nrt.file_path,
            title_size=35,
        )
        editor.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        config_window.grid_rowconfigure(0, weight=1)
        config_window.grid_columnconfigure(0, weight=1)
