from datetime import datetime
from pathlib import Path
from tkinter import ttk

import customtkinter as ctk
from ctdam.entry.gui.toml_editor import TomlEditor

from ctdclient.definitions import CONFIG_PATH
from ctdclient.view.View import ViewMixin


class NRTConfigurator(ViewMixin, TomlEditor):
    def __init__(
        self,
        master,
        title: str = "NRT Configuration",
        possible_parameters: list[str] = [
            "recipient_address",
            "target_file_directory",
            "target_file_suffix",
            "frequency_of_action",
            "geo_filter",
        ],
        config_file: Path | str = "",
        title_size: int = 20,
        possible_email_parameters: list[str] = [
            "open_draft",
            "smtp_server",
            "smtp_port",
            "smtp_email",
            "subject",
            "body",
        ],
    ):
        super().__init__(
            master,
            title,
            possible_parameters,
            config_file,
            title_size,
            fg_color="gray16",
            default_dir_to_save_in=CONFIG_PATH,
        )
        self.possible_email_parameters = possible_email_parameters
        self.configure(fg_color="gray16")

    def load_config_specific_data(self, row=0):
        section = (
            "ftp_info"
            if self.config_data.get("method") == "ftp"
            else "email_info"
        )
        frame = ctk.CTkFrame(self.content_frame, fg_color="gray16")
        frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
        frame.grid_columnconfigure(0, weight=1)
        ttk.Separator(frame, orient="horizontal").grid(
            row=0, column=0, columnspan=3, sticky="ew"
        )
        header = ctk.CTkLabel(
            frame,
            text=(
                "FTP configuration"
                if section == "ftp_info"
                else "Email configuration"
            ),
            font=("Arial", 14, "bold"),
        )
        header.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        for index, (key, value) in enumerate(
            self.config_data.get(section, {}).items(), start=2
        ):
            self.create_info_param(frame, section, key, value, index)

    def create_info_param(self, frame, section, key, value, row):
        frame = ctk.CTkFrame(frame, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
        frame.grid_columnconfigure(0, weight=1)

        key_label = ctk.CTkLabel(frame, text=key.replace("_", " "), anchor="w")
        key_label.grid(row=0, column=0, sticky="w", padx=2, pady=2)

        if section == "email_info" and key == "body":
            value_entry = ctk.CTkTextbox(frame, height=200, width=300)
            value_entry.insert(1.0, value)
            args = {"index1": "1.0", "index2": "end"}
        elif section == "email_info" and key == "open_draft":
            switch_var = ctk.StringVar(value=value)
            value_entry = ctk.CTkSwitch(
                frame,
                variable=switch_var,
                text="",
                onvalue="true",
                offvalue="false",
            )
        else:
            value_entry = ctk.CTkEntry(frame, width=300)
            value_entry.insert(0, value)
            if section == "ftp_info" and key == "password":
                value_entry.configure(show="*")
            args = {}
        value_entry.grid(row=0, column=1)

        def update_param(event=None):
            if key == "open_draft":
                self.config_data[section][key] = switch_var.get()
            else:
                self.config_data[section][key] = value_entry.get(**args)

        key_label.bind("<Leave>", update_param)
        value_entry.bind("<Leave>", update_param)
        value_entry.bind("<FocusOut>", update_param)
        if key == "open_draft":
            value_entry.configure(command=update_param)

    def check_input(self) -> bool:
        # check frequency_of_action
        input = self.config_data["frequency_of_action"]
        if not input == "each_processing":
            try:
                datetime.strptime(input, "%H:%M:%S")
            except Exception:
                self.bad_input_warning(
                    f'Incorrect frequency of action format: {
                        input
                    }. Expected either each_processing or "HH:MM:SS"'
                )
                return False
        if self.config_data.get("method") == "ftp":
            try:
                port = int(self.config_data["ftp_info"]["port"])
                if not 1 <= port <= 65535:
                    raise ValueError
            except (KeyError, TypeError, ValueError):
                self.bad_input_warning(
                    "FTP port must be a number from 1 to 65535."
                )
                return False
            self.config_data["ftp_info"]["port"] = port
            return True
        # check open_draft
        input = self.config_data["email_info"]["open_draft"]
        if input.lower() not in ["true", "false", ""]:
            self.bad_input_warning(
                f"Incorrect open_draft format: {
                    input
                }. Expected either true or false as strings."
            )
            return False
        return True


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("ctktheme.json")

    app = ctk.CTk()
    app.geometry("800x600")

    editor = NRTConfigurator(
        app,
        config_file="nrt_coriolis.toml",
        title_size=35,
    )

    editor.grid(row=0, column=0, sticky="nsew")

    # Configure the grid to make the editor expand with the window
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)
    app.mainloop()
