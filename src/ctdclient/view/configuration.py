from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import tkinter.font as tkFont
import customtkinter as ctk
from functools import partial
from ctdclient.view.View import ViewMixin
from ctdclient.configurationhandler import ConfigurationFile


class ConfigurationView(ctk.CTkFrame, ViewMixin):
    """ """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        configuration: ConfigurationFile,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self.configuration = configuration
        self.values_to_set = self.get_values_to_set()
        self.padx = 5
        self.pady = 5
        setting_frame = self.setting_frame()
        setting_frame.grid()

    def get_values_to_set(self):
        value_dict = {}
        for instrument in self.configuration.platforms:
            value_dict.update(
                {
                    instrument: {
                        key: tk.StringVar(value=value)
                        for key, value in self.configuration[
                            instrument.lower()
                        ]["paths"].items()
                    }
                }
            )
        value_dict.update(
            {
                "operators": {
                    key: tk.StringVar(value=value)
                    for key, value in self.configuration.operators.items()
                }
            }
        )
        return value_dict

    def setting_frame(self):
        frame = ctk.CTkFrame(self)
        for index, (instrument, inner_dict) in enumerate(
            self.values_to_set.items()
        ):
            index *= len(inner_dict) + 2
            ctk.CTkLabel(
                frame,
                text=f"{instrument}",
                font=(tkFont.nametofont("TkDefaultFont"), 20),
            ).grid(
                row=index,
                column=0,
                sticky=tk.W,
                padx=self.padx,
                pady=self.pady,
            )
            ttk.Separator(frame, orient="horizontal").grid(
                row=index + 1, sticky=tk.E + tk.W
            )
            for inner_index, (name, variable) in enumerate(inner_dict.items()):
                row = index + inner_index + 2
                ctk.CTkLabel(frame, text=f"{name.replace('_', ' ')}: ").grid(
                    row=row,
                    column=0,
                    sticky=tk.W,
                    padx=self.padx,
                    pady=self.pady,
                )
                if instrument == "operators":
                    ctk.CTkEntry(frame, textvariable=variable).grid(
                        row=row,
                        column=1,
                        sticky=tk.E,
                        padx=self.padx,
                        pady=self.pady,
                    )
                else:
                    ctk.CTkLabel(
                        frame,
                        textvariable=variable,
                        font=(tkFont.nametofont("TkDefaultFont"), 10),
                    ).grid(
                        row=row,
                        column=1,
                        sticky=tk.E,
                        padx=self.padx,
                        pady=self.pady,
                    )
                    command_with_arguments = partial(
                        self.select_file, instrument, name, variable
                    )
                    ctk.CTkButton(
                        frame,
                        text="Browse",
                        command=command_with_arguments,
                        width=28,
                    ).grid(row=row, column=2, padx=self.padx, pady=self.pady)
        ctk.CTkButton(
            frame, text="Set operators", command=self.write_config, width=600
        ).grid(row=row, column=0, columnspan=3, padx=self.padx, pady=self.pady)
        return frame

    def write_config(self):
        self.configuration["operators"] = {
            key: value.get()
            for key, value in self.values_to_set["operators"].items()
        }
        self.configuration.write(use_internal_values=False)

    def select_file(self, instrument, name, variable):
        """
        Generic file selection method, that opens a file browsing pop-up.
        """
        if not name.endswith("directory"):
            if name.endswith("psa"):
                file_type = "psa"
            elif name.startswith("batch"):
                file_type = "bat"
            else:
                file_type = name
            path = Path(variable.get())
            filetypes = (
                (f"{file_type} files", f"*.{file_type}"),
                ("All files", "*.*"),
            )

            file = fd.askopenfilename(
                title=f"Path to {name}",
                initialdir=path.parent,
                initialfile=path.name,
                filetypes=filetypes,
            )
        else:
            file = fd.askdirectory(
                title=f"{name}",
                initialdir=variable.get(),
            )
        if file:
            variable.set(file)
            self.configuration[instrument.lower()]["paths"][name] = file
            self.configuration.write(use_internal_values=False)
