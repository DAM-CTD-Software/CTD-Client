from datetime import datetime
from pathlib import Path
from tkinter import ttk

import customtkinter as ctk
from ctdclient.definitions import event_manager
from ctdclient.view.View import ViewMixin
from processing.gui.toml_editor import TomlEditor


class NRTConfigurator(ViewMixin, TomlEditor):
    def __init__(
        self,
        master,
        title: str = "NRT Configuration",
        possible_parameters: list[str] = [
            "recipient_name",
            "recipient_address",
            "target_file_directory",
            "target_file_suffix",
            "frequency_of_action",
            "geo_filter",
        ],
        config_file: Path | str = "",
        title_size: int = 20,
        possible_email_parameters: list[str] = [
            "send_directly",
            "smtp_server",
            "smtp_port",
            "smtp_email",
            "smtp_user",
            "smtp_pass",
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
        )
        self.possible_email_parameters = possible_email_parameters
        master.protocol("WM_DELETE_WINDOW", self.cancel)

    def cancel(self):
        for frame in self.winfo_children():
            try:
                frame.grid_forget()
            except AttributeError:
                pass
            frame.destroy()
        event_manager.publish("kill_nrt_config")

    def load_config_specific_data(self, row=0):
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
        frame.grid_columnconfigure(0, weight=1)
        ttk.Separator(frame, orient="horizontal").grid(
            row=0, column=0, columnspan=3, sticky="ew"
        )
        header = ctk.CTkLabel(
            frame,
            text="Email configuration",
            font=("Arial", 14, "bold"),
        )
        header.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        if "email_info" in self.config_data:
            for key, value in self.config_data["email_info"].items():
                self.create_email_info_param(frame, key, value, row)
                row += 1

    def create_email_info_param(self, frame, key, value, row):
        if not row:
            row = len(frame.winfo_children())

        frame = ctk.CTkFrame(frame, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
        frame.grid_columnconfigure(0, weight=1)

        key_label = ctk.CTkLabel(frame, text=key, anchor="w")
        key_label.grid(row=0, column=0, sticky="w", padx=2, pady=2)

        if key == "body":
            value_entry = ctk.CTkTextbox(frame, height=200, width=300)
            value_entry.insert(1.0, value)
            args = {"index1": "1.0", "index2": "end"}
        else:
            value_entry = ctk.CTkEntry(frame, width=300)
            value_entry.insert(0, value)
            args = {}
        value_entry.grid(row=0, column=1)  # , padx=5, pady=5)

        def update_param(event):
            self.config_data["email_info"][key] = value_entry.get(**args)

        key_label.bind("<Leave>", update_param)
        value_entry.bind("<Leave>", update_param)
        frame.grid(row=row + 1, column=0, columnspan=3, sticky="ew")

    def check_input(self) -> bool:
        # check frequency_of_action
        input = self.config_data["frequency_of_action"]
        if not input == "each_processing":
            try:
                datetime.strptime(input, "%H:%M:%S")
            except Exception:
                self.bad_input_warning(
                    f'Incorrect frequency of action format: {
                        input}. Expected either each_processing or "HH:MM:SS"'
                )
                return False
        # check open_draft
        input = self.config_data["email_info"]["open_draft"]
        if input.lower() not in ["true", "false"]:
            self.bad_input_warning(
                f"Incorrect open_draft format: {
                    input}. Expected either True or False as strings."
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
