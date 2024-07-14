import tkinter as tk
from pathlib import Path
from tkinter import filedialog as fd

import customtkinter as ctk
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.View import ViewMixin


class ProcessingConfigFrame(ViewMixin, CtkFrame):

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        ctk.CTkButton(
            self,
            text="Save current configuration",
            command=self.save_current_configuration,
        ).grid(row=0, column=0, sticky=tk.W, pady=10)
        ctk.CTkButton(
            self, text="Load configuration", command=self.load_configuration
        ).grid(row=0, column=1, sticky=tk.E, pady=10)
        self.grid()

    def save_current_configuration(self):
        current_file = Path(self.file_path.get())
        new_file_name = fd.asksaveasfilename(
            title="Save new config as",
            initialdir=current_file.parent,
            initialfile=current_file.name,
            defaultextension=".toml",
            filetypes=[
                ("toml file", ".toml"),
                ("batch script", ".bat"),
                ("All files", ".*"),
            ],
        )
        if new_file_name:
            self.file_path.set(new_file_name)
            processing_dict = {
                key: value.get()
                for key, value in self.path_dict.items()
                if key not in self.processing.optional_options.keys()
            }
            optional_dict = {
                key: value.get()
                for key, value in self.path_dict.items()
                if key in self.processing.optional_options.keys()
            }
            processing_dict = {
                **processing_dict,
                "optional": optional_dict,
                "modules": self.export_module_and_psa_info(),
            }
            self.processing.file_path = new_file_name
            self.processing.save(processing_dict)
            self.path_frame.grid_forget()
            self.path_frame.destroy()
            self.update_values()

    def load_configuration(self):
        if self.select_file("toml", self.file_path):
            path_to_file = Path(self.file_path.get())
            if path_to_file.suffix == ".toml":
                if self.processing.load(path_to_file=path_to_file):
                    self.processing.use_custom_script = False
                    self.path_frame.grid_forget()
                    self.path_frame.destroy()
                    self.update_values()
                else:
                    # TODO: open a message window
                    pass
            # allow custom scripts
            else:
                self.processing.use_custom_script = path_to_file
                self.path_frame.grid_forget()
                self.path_frame.destroy()
                self.file_path.set(str(path_to_file))
                self.path_frame = self.custom_srcipt_frame()
