import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog as fd

import customtkinter as ctk
import psutil
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.View import ViewMixin
from CTkMessagebox import CTkMessagebox


class RunFrame(ViewMixin, CtkFrame):
    """
    Frame that wraps the seasave.exe start button with two checkboxes for
    the command line options.

    Parameters
    ----------
    window :


    Returns
    -------

    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        for arg in args:
            if arg.__class__.__name__ == "MeasurementView":
                self.last_filename = arg.last_filename
                self.current_filename = arg.current_filename
                self.initialize()

    def initialize(self):
        self.downcast_option = self.configuration.downcast_option
        self.autostart = tk.BooleanVar(value=True)
        self.downcast = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self,
            text="autostart",
            variable=self.autostart,
        ).grid(row=0, pady=2)
        row = 1
        if self.downcast_option:
            ctk.CTkCheckBox(
                self,
                text="downcast",
                variable=self.downcast,
            ).grid(row=row)
            row += 1
        ctk.CTkButton(
            self,
            text="Start Seasave",
            command=self.start_seasave,
        ).grid(row=row, column=0, sticky=tk.W, padx=20, pady=5)
        self.processing_button = ctk.CTkButton(
            self, text="Run Processing", command=self.processing_thread
        )
        self.processing_button.grid(
            row=row, column=1, sticky=tk.E, padx=20, pady=5
        )
        self.grid()

    def start_seasave(self):
        """
        Method that is called upon clicking 'Start Seasave'. Organizes
        the information flow of bottle closing information and dship metadata.
        """
        # pre-run check
        if self.process_exists("seasave"):
            CTkMessagebox(
                title="Warning",
                message="Seasave is already running!",
                icon="warning",
                option_1="Ok",
            )
            return
        if (self.current_filename.get() == self.last_filename.get()) and Path(
            self.last_filename.get()
        ).exists():
            msg = CTkMessagebox(
                title="Warning",
                message=f"Caution! Do you really want to override the last filename {
                    self.last_filename.get()}?",
                icon="warning",
                option_1="Cancel",
                option_2="Yes",
            )
            if msg.get() == "Cancel":
                return

        # run
        self.process = self.callbacks["runseasave"](
            self.current_filename.get(),
            self.downcast.get(),
            self.autostart.get(),
        )
        self.check_seasave()

    def check_seasave(self):
        if self.process.poll() is not None:
            self.callbacks["postruncheck"]()
        else:
            self.after(1000, self.check_seasave)

    def process_exists(self, process_name: str) -> bool:
        progs = {p.info["name"].lower() for p in psutil.process_iter(["name"])}
        if process_name in progs:
            return True
        else:
            return False

    def update_button(self):
        if self.proc_thread.is_alive():
            button_name = "Cancel"
            button_command = self.cancel_processing
            self.processing_button.after(1000, self.update_button)
        else:
            button_name = "Run Processing"
            button_command = self.processing_thread
        self.processing_button.configure(
            text=button_name, command=button_command
        )

    def processing_thread(self):
        self.proc_thread = threading.Thread(target=self.run_processing)
        self.proc_thread.start()
        self.update_button()

    def run_processing(self):
        """Collects the processing step information and feeds it into the
        batch processing routine."""
        self.configuration.reload()
        hex_file = tk.StringVar(value=str(self.configuration.last_filename))
        selected_file = self.select_file("hex", hex_file)
        if selected_file:
            try:
                self.processing.input_file = hex_file.get()
                self.processing.run()
            except TypeError:
                pass
            else:
                self.configuration.last_processing_file = (
                    self.processing.file_path
                )
                self.configuration.write()

    def cancel_processing(self):
        self.processing.cancel()

    def select_file(self, file_type: str, variable: tk.StringVar):
        """
        Generic file selection method, that opens a file browsing pop-up.
        """
        path = Path(variable.get())
        filetypes = (
            (f"{file_type} files", f"*.{file_type}"),
            ("All files", "*.*"),
        )
        file = fd.askopenfilename(
            title=f"Path to {file_type}",
            initialdir=path.parent,
            initialfile=path.name,
            filetypes=filetypes,
        )
        if file:
            variable.set(file)
            return True
        else:
            return False
