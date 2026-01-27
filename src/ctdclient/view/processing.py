from __future__ import annotations

import logging
import sys
import tkinter as tk
import tkinter.font as tkFont
from pathlib import Path
from tkinter import filedialog as fd
from typing import Callable

import customtkinter as ctk
from processing.gui.procedure_config_view import ProcedureConfigView

from ctdclient.definitions import CONFIG_PATH, ICON_PATH, config
from ctdclient.model.processing import ProcessingConfig, ProcessingProcedure
from ctdclient.utils import call_editor
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.View import ViewMixin

logger = logging.getLogger(__name__)


class ProcessingView(ViewMixin, CtkFrame):
    """
    A frame to wrap all information and functionality for data processing.
    Is divided in two main parts, the configuration of input paths, to xmlcon,
    hex and psa folder, and the selection of processing modules and their
    respective psas.
    """

    def initialize(self, root):
        super().__init__(master=root)

    def populate(self, processing_list: list):
        for frame in self.winfo_children():
            try:
                frame.grid_forget()
            except AttributeError:
                pass
            frame.destroy()
        row = 0
        if len(processing_list) == 0:
            header = ctk.CTkLabel(
                self,
                text="No processing configured.",
                font=(tkFont.nametofont("TkDefaultFont"), 20),
            )
            header.grid()
            row += 1
        new_processing = ctk.CTkButton(
            self,
            text="Create new processing workflow",
            command=self.open_template,
        )
        new_processing.grid(
            row=row, column=0, sticky="ew", padx=self.padx, pady=self.pady
        )
        for index, processing in enumerate(processing_list, start=row + 1):
            self.create_processing_entry(processing, index)
            row = index

        ctk.CTkLabel(
            self,
            text="General Settings:",
            font=(tkFont.nametofont("TkDefaultFont"), 20),
        ).grid(
            row=row + 1, column=0, sticky="w", padx=self.padx, pady=self.pady
        )

        settings_frame = ctk.CTkFrame(
            self, fg_color="transparent", border_width=1, border_color="gray10"
        )
        settings_frame.grid(
            row=row + 2, column=0, sticky="ew", padx=self.padx, pady=self.pady
        )

        for index, (key, value) in enumerate(config.processing.items()):
            self.settings_entry(settings_frame, key, value, index)

    def settings_entry(self, parent_frame, key, value, row):
        frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        frame.grid(
            row=row, column=0, sticky="ew", padx=self.padx, pady=self.pady
        )
        frame.grid_columnconfigure(0, weight=1)
        # name = ctk.CTkLabel(frame, text=key, anchor="w", justify="left")
        # name.grid(row=0, column=0, padx=self.padx, pady=self.pady, sticky="w")
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
            config.processing[key] = entry.get()
            if key == "auto_process":
                self.toggle_auto_process(entry.get())

        if key.endswith(("dir", "fingerprint")):
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

    def toggle_auto_process(self, new_value: str):
        self.callbacks["update_auto_process"](new_value)

    def open_template(self):
        template = self.callbacks["new_processing"]()
        if template:
            self.open_config(template)

    def create_processing_entry(
        self, processing_workflow: ProcessingConfig, row: int
    ):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(
            row=row, column=0, sticky="ew", padx=self.padx, pady=self.pady
        )
        frame.grid_columnconfigure(0, weight=1)

        name = ctk.CTkLabel(
            frame, text=processing_workflow.name, anchor="w", justify="left"
        )
        name.grid(row=0, column=0, padx=self.padx, pady=self.pady, sticky="w")

        if isinstance(processing_workflow, ProcessingProcedure):

            def toggle_entry():
                global hidden
                if hidden:
                    info.grid(
                        row=1,
                        column=0,
                        padx=self.padx,
                        pady=self.pady,
                        sticky="w",
                    )
                else:
                    info.grid_remove()
                hidden = not hidden

            global hidden
            hidden = True

            info_toggle = ctk.CTkButton(
                frame,
                text="show/hide modules",
                command=lambda: toggle_entry(),
            )
            info_toggle.grid(row=0, column=1, padx=self.padx, pady=self.pady)

            info = ctk.CTkFrame(
                frame,
                fg_color="transparent",
            )
            self.display_modules(info, processing_workflow)

            config = ctk.CTkButton(
                frame,
                text="edit/details",
                command=lambda: self.open_config(processing_workflow),
            )
            config.grid(row=0, column=2, padx=self.padx, pady=self.pady)

        else:
            open_editor = ctk.CTkButton(
                frame,
                text="open editor",
                command=lambda: call_editor(
                    processing_workflow.path_to_config
                ),
            )
            open_editor.grid(row=0, column=2, padx=self.padx, pady=self.pady)

        delete = ctk.CTkButton(
            frame,
            text="Delete",
            command=lambda: self.callbacks["delete_processing"](
                processing_workflow
            ),
        )
        delete.grid(row=0, column=3, padx=self.padx, pady=self.pady)

        run = ctk.CTkSwitch(
            frame,
            text="",
            command=lambda: self.callbacks["toggle_active"](
                processing_workflow
            ),
        )
        run.grid(row=0, column=4, padx=self.padx, pady=self.pady)

        if processing_workflow.active:
            run.select()

    def display_modules(
        self, frame: ctk.CTkFrame, processing_workflow: ProcessingProcedure
    ):
        for index, module in enumerate(processing_workflow.modules.keys()):
            ctk.CTkLabel(frame, text=module).grid(row=index, column=0)

    def open_config(self, processing_workflow: ProcessingConfig):
        config_window = ctk.CTkToplevel(self)

        editor = ProcedureConfigView(
            master=config_window,
            config_file=processing_workflow.path_to_config,
            possible_parameters=[
                "psa_directory",
                "output_dir",
            ],
            title_size=35,
            default_dir_to_save_in=CONFIG_PATH,
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
            command=lambda e: self.callbacks["update_processing_workflows"](),
        )
        config_window.title(
            f"Configuration of processing workflow {processing_workflow.name}"
        )
        if sys.platform.startswith("win"):
            config_window.after(
                200, lambda: config_window.iconbitmap(ICON_PATH)
            )
        config_window.grid_rowconfigure(0, weight=1)
        config_window.grid_columnconfigure(0, weight=1)
        config_window.geometry("700x850")
        config_window.grab_set()
