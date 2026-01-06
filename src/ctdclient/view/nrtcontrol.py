import sys
import tkinter.font as tkFont

import customtkinter as ctk

from ctdclient.definitions import ICON_PATH
from ctdclient.model.near_real_time_publication import NearRealTimeTarget
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.nrtconfig import NRTConfigurator
from ctdclient.view.View import ViewMixin


class NRTControlFrame(ViewMixin, CtkFrame):
    def initialize(self, root):
        super().__init__(master=root)

    def reload(self):
        self.callbacks["update_nrts"]()

    def instantiate(self, nrt_list: list):
        # clean slate before refilling the frame
        for frame in self.winfo_children():
            try:
                frame.grid_forget()
            except AttributeError:
                pass
            frame.destroy()
        row = 0
        if len(nrt_list) == 0:
            header = ctk.CTkLabel(
                self,
                text="No NRT publications configured.",
                font=(tkFont.nametofont("TkDefaultFont"), 20),
            )
            header.grid()
            row += 1
        new_nrt_pub = ctk.CTkButton(
            self,
            text="Create new NRT publication",
            command=self.open_template,
        )
        new_nrt_pub.grid(
            row=row, column=0, sticky="ew", padx=self.padx, pady=self.pady
        )
        for index, nrt in enumerate(nrt_list, start=row + 1):
            self.create_nrt_overview(nrt, index)

    def open_template(self):
        template = self.callbacks["get_template"]()
        if template:
            self.open_config(template)

    def create_nrt_overview(self, nrt: NearRealTimeTarget, row: int):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(
            row=row, column=0, sticky="ew", padx=self.padx, pady=self.pady
        )
        frame.grid_columnconfigure(0, weight=1)

        name = ctk.CTkLabel(frame, text=nrt.name)
        name.grid(row=0, column=0, padx=self.padx, pady=self.pady)

        status = ctk.CTkLabel(
            frame,
            text="Active" if nrt.active else "Inactive",
            text_color="green" if nrt.active else "red",
        )
        status.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        config = ctk.CTkButton(
            frame, text="open config", command=lambda: self.open_config(nrt)
        )
        config.grid(row=0, column=2, padx=self.padx, pady=self.pady)

        toggle_status = ctk.CTkButton(
            frame,
            text="Deactivate" if nrt.active else "Activate",
            command=lambda: self.callbacks["toggle_activity"](
                nrt, status, toggle_status
            ),
        )
        toggle_status.grid(row=0, column=3, padx=self.padx, pady=self.pady)

        send_mail = ctk.CTkButton(
            frame,
            text="Send mail",
            command=lambda: self.callbacks["send_email"](nrt),
        )
        send_mail.grid(row=0, column=4, padx=self.padx, pady=self.pady)
        delete = ctk.CTkButton(
            frame,
            text="Delete",
            command=lambda: self.callbacks["delete_nrt"](nrt),
        )
        delete.grid(row=0, column=5, padx=self.padx, pady=self.pady)

    def toggle_activity_state(
        self,
        nrt: NearRealTimeTarget,
        status_line: ctk.CTkLabel,
        status_button: ctk.CTkButton,
    ):
        status_line.configure(
            text="Active" if nrt.active else "Inactive",
            text_color="green" if nrt.active else "red",
            require_redraw=True,
        )
        status_button.configure(
            text="Deactivate" if nrt.active else "Activate",
            require_redraw=True,
        )

    def open_config(self, nrt: NearRealTimeTarget):
        config_window = ctk.CTkToplevel(self)

        editor = NRTConfigurator(
            config_window,
            config_file=nrt.file_path,
            title_size=35,
        )
        editor.grid(
            row=0,
            column=0,
            sticky="nswe",
            padx=self.padx,
            pady=self.pady,
        )
        editor.bind(
            "<Destroy>",
            command=lambda e: self.callbacks["update_nrts"](),
        )

        config_window.title(f"NRT configuration of {nrt.file_path}")
        if sys.platform.startswith("win"):
            config_window.after(
                200, lambda: config_window.iconbitmap(ICON_PATH)
            )
        config_window.grid_rowconfigure(0, weight=1)
        config_window.grid_columnconfigure(0, weight=1)
        config_window.geometry("700x850")
        config_window.grab_set()
