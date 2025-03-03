from __future__ import annotations

import sys
import tkinter.font as tkFont

import customtkinter as ctk
from code_tools.logging import get_logger
from ctdclient.definitions import ICON_PATH
from ctdclient.model.processing import ProcessingConfig
from ctdclient.model.processing import ProcessingProcedure
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.View import ViewMixin
from processing.gui.procedure_config_view import ProcedureConfigView

logger = get_logger(__name__)


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
        name.grid(row=0, column=0, padx=self.padx, pady=self.pady)

        if isinstance(processing_workflow, ProcessingProcedure):

            def toggle_entry():
                global hidden
                if hidden:
                    info.grid(row=1, column=0, padx=self.padx, pady=self.pady)
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
        )
        run.grid(row=0, column=4, padx=self.padx, pady=self.pady)

        if processing_workflow.active:
            run.select()

    def display_modules(
        self, frame: ctk.CTkFrame, processing_workflow: ProcessingProcedure
    ):
        for index, module in enumerate(
            processing_workflow.procedure.modules.keys()
        ):
            ctk.CTkLabel(frame, text=module).grid(row=index, column=0)

    def open_config(self, processing_workflow: ProcessingConfig):
        config_window = ctk.CTkToplevel(self)

        editor = ProcedureConfigView(
            master=config_window,
            config_file=processing_workflow.path_to_config,
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
