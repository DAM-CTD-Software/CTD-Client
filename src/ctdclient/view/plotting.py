import tkinter as tk
import tkinter.font as tkFont
from pathlib import Path
from tkinter import filedialog as fd
from typing import Callable

import customtkinter as ctk
from ctdclient.definitions import config
from ctdclient.definitions import CONFIG_PATH
from ctdclient.utils import call_editor
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.View import ViewMixin
from CTkMessagebox import CTkMessagebox


class PlottingFrame(ViewMixin, CtkFrame):
    def initialize(self, root):
        super().__init__(master=root)

        option_desc = ctk.CTkLabel(
            self,
            text="Cruise plot settings:",
            font=(tkFont.nametofont("TkDefaultFont"), 20),
        )
        option_desc.grid(row=0, sticky=tk.W)

        self.option_frame = ctk.CTkFrame(
            self, fg_color="transparent", border_width=1, border_color="gray10"
        )
        self.option_frame.grid(row=1)

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=2)

        plot = ctk.CTkButton(
            self.button_frame, text="Plot a file", command=self.plot_file
        )
        plot.grid(row=0, column=0, sticky=tk.W, padx=20, pady=20)

        cruise_plot = ctk.CTkButton(
            self.button_frame, text="Plot the cruise", command=self.plot_cruise
        )
        cruise_plot.grid(row=0, column=1, sticky=tk.E, padx=20, pady=20)

        config_button = ctk.CTkButton(
            self.button_frame,
            text="Config colors/ranges",
            command=self.open_config,
        )
        config_button.grid(row=0, column=2, sticky=tk.E, padx=20, pady=20)

        self.display_options()

    def display_options(self):
        for widget in self.option_frame.winfo_children():
            widget.destroy()
        row_index = 0
        for key, value in config.plotting.items():
            self.create_key_value_field(
                self.option_frame, key, value, row=row_index
            )
            row_index += 1

    def create_key_value_field(self, parent, key, value, row):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        frame.grid_columnconfigure(0, weight=1)

        key_label = ctk.CTkLabel(frame, text=key.replace("_", " "), anchor="w")
        key_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)

        if type(value) is bool:
            entry = ctk.CTkSwitch(
                frame,
                text="",
                onvalue=True,
                offvalue=False,
            )
            entry.grid(row=0, column=2)
            if value:
                entry.select()
            else:
                entry.deselect()
        else:
            entry = ctk.CTkEntry(frame, width=300)
            entry.grid(row=0, column=2)
            entry.insert(0, value)
            entry.xview(tk.END)

        def update_value(event=None):
            config.plotting[key] = entry.get()
            if key == "auto_plot":
                self.toggle_auto_plot(entry.get())

        if "dir" in key:
            file_picker = self.create_picker_element(
                frame=frame,
                entry=entry,
                callback=update_value,
            )
            file_picker.grid(row=0, column=1, padx=5, pady=5)

        entry.bind("<FocusOut>", update_value)
        entry.bind("<Leave>", update_value)

    def create_picker_element(
        self,
        frame: ctk.CTkFrame,
        entry: ctk.CTkEntry,
        directory: bool = True,
        callback: Callable | None = None,
        initial_dir: Path | str | None = None,
    ) -> ctk.CTkButton:
        if directory:
            command = fd.askdirectory
            text = "Pick directory"
            width = 80
        else:
            command = fd.askopenfilename
            text = "Pick file"
            width = 60

        def open_file_picker():
            entry.delete(0, tk.END)
            entry.insert(0, command(initialdir=initial_dir))
            entry.xview(tk.END)
            if isinstance(callback, Callable):
                callback()

        return ctk.CTkButton(
            frame, command=open_file_picker, text=text, width=width
        )

    def plot_file(self):
        file = fd.askopenfilename(
            title="Open a file for plotting",
            initialdir=config.output_directory,
            initialfile=config.last_filename,
            filetypes=[("cnv files", "*.cnv")],
        )
        if file:
            # warn before plotting large files
            size_limit = int(config.plotting["size_limit"])
            file_size = Path(file).stat().st_size // 1000000
            if file_size > size_limit:
                answer = CTkMessagebox(
                    title=f"Large file (above {size_limit}MB)",
                    icon="cancel",
                    message=f"This is a very large file with a size of {file_size}MB. This can lead to long plotting times. Are you sure that you want to continue?",
                    option_1="Ok",
                    option_2="Cancel",
                )
                if answer.get() != "Ok":
                    return

            self.callbacks["plot_file"](file)

    def plot_cruise(self):
        dir = fd.askdirectory(
            title="Pick a cruise directory to plot",
            initialdir=config.output_directory,
        )
        if dir:
            self.callbacks["plot_cruise"](str(dir))

    def toggle_auto_plot(self, new_value: str):
        self.callbacks["update_auto_plot"](new_value)

    def open_config(self):
        call_editor(CONFIG_PATH.joinpath("vis_config.toml"))
