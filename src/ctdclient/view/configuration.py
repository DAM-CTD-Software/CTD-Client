import tkinter as tk
import tkinter.font as tkFont
from functools import partial
from pathlib import Path
from tkinter import filedialog as fd
from tkinter import ttk

import customtkinter as ctk
from ctdclient.definitions import config
from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.tabview import TabView
from ctdclient.view.View import ViewMixin
from CTkListbox import CTkListbox
from CTkMessagebox import CTkMessagebox


class ConfigurationView(ViewMixin, CtkFrame):
    """ """

    def initialize(self, root):
        super().__init__(master=root)
        self.base_settings = BaseSettings(self)
        self.expert_settings = ExpertSettings(self)
        self.contact_view = ContactView(self)
        self.tabs = TabView(
            window=self,
            tabs={
                "basic settings": self.base_settings,
                "expert settings": self.expert_settings,
                "contact": self.contact_view,
            },
            width=600,
            height=700,
        )
        self.tabs.grid()


class BaseSettings(ViewMixin, CtkFrame):

    def initialize(self, root):
        super().__init__(master=root)
        self.values_to_set = self.get_values_to_set()
        for index, (instrument, inner_dict) in enumerate(
            self.values_to_set.items()
        ):
            index *= len(inner_dict) + 2
            ctk.CTkLabel(
                self,
                text=f"{instrument}",
                font=(tkFont.nametofont("TkDefaultFont"), 20),
            ).grid(
                row=index,
                column=0,
                sticky=tk.W,
                padx=self.padx,
                pady=self.pady,
            )
            ttk.Separator(self, orient="horizontal").grid(
                row=index + 1, sticky=tk.E + tk.W
            )
            for inner_index, (name, variable) in enumerate(inner_dict.items()):
                row = index + inner_index + 2
                ctk.CTkLabel(self, text=f"{name.replace('_', ' ')}: ").grid(
                    row=row,
                    column=0,
                    sticky=tk.W,
                    padx=self.padx,
                    pady=self.pady,
                )
                if instrument == "operators":
                    ctk.CTkEntry(self, textvariable=variable).grid(
                        row=row,
                        column=1,
                        sticky=tk.E,
                        padx=self.padx,
                        pady=self.pady,
                    )
                else:
                    if name == "number_of_bottles":
                        variable = tk.IntVar(value=int(variable.get()))
                        inner_dict[name] = variable
                        ctk.CTkEntry(self, textvariable=variable).grid(
                            row=row,
                            column=1,
                            sticky=tk.E,
                            padx=self.padx,
                            pady=self.pady,
                        )
                    else:
                        ctk.CTkLabel(
                            self,
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
                            self,
                            text="Browse",
                            command=command_with_arguments,
                            width=28,
                        ).grid(
                            row=row, column=2, padx=self.padx, pady=self.pady
                        )
        ctk.CTkButton(
            self, text="Save", command=self.write_config, width=600
        ).grid(row=row, column=0, columnspan=3, padx=self.padx, pady=self.pady)

    def get_values_to_set(self):
        value_dict = {}
        for instrument in self.configuration.platforms:
            if instrument == "CTD":
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

    def write_config(self, instrument: str = "CTD"):
        self.configuration["operators"] = {
            key: value.get()
            for key, value in self.values_to_set["operators"].items()
        }
        self.configuration[instrument.lower()]["paths"] = {
            key: value.get()
            for key, value in self.values_to_set[instrument].items()
        }
        self.configuration.write(use_internal_values=False)
        print("saved")
        self.callbacks["save"]()

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


class ExpertSettings(ctk.CTkScrollableFrame):
    def initialize(self, root):
        super().__init__(master=root)
        self.configuration = config
        self.configure(
            height=500,
            width=600,
            border_width=1,
            border_color="gray10",
            fg_color="transparent",
        )
        self.padx = 5
        self.pady = 5
        self.values = self.get_values_to_set()
        self.platform_options = ["CTD"]  # ¨Scanfish¨
        top_entry_length = len(self.values["base"])
        for index, (setting, inner_dict) in enumerate(self.values.items()):
            index *= top_entry_length + len(self.platform_options) + 1
            ctk.CTkLabel(
                self,
                text=f"{setting}",
                font=(tkFont.nametofont("TkDefaultFont"), 20),
            ).grid(
                row=index,
                column=0,
                sticky=tk.W,
                padx=self.padx,
                pady=self.pady,
            )
            ttk.Separator(self, orient="horizontal").grid(
                row=index + 1, sticky=tk.E + tk.W
            )
            for inner_index, (name, (variable, param_type)) in enumerate(
                inner_dict.items()
            ):
                row = index + inner_index + 2
                ctk.CTkLabel(self, text=f"{name.replace('_', ' ')}: ").grid(
                    row=row,
                    column=0,
                    sticky=tk.W,
                    padx=self.padx,
                    pady=self.pady,
                )
                if param_type == bool:
                    variable = tk.BooleanVar(value=variable.get())
                    inner_dict[name] = (variable, param_type)
                    ctk.CTkSwitch(
                        self,
                        variable=variable,
                        text="",
                    ).grid(
                        row=row,
                        column=1,
                        sticky=tk.E,
                        padx=self.padx,
                        pady=self.pady,
                    )
                elif name.endswith("exe"):
                    ctk.CTkLabel(
                        self,
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
                        self.select_file, setting, name, variable
                    )
                    ctk.CTkButton(
                        self,
                        text="Browse",
                        command=command_with_arguments,
                        width=28,
                        font=(tkFont.nametofont("TkDefaultFont"), 10),
                    ).grid(row=row, column=2, padx=self.padx, pady=self.pady)
                elif name.endswith("platforms"):
                    self.listbox = CTkListbox(
                        self,
                        multiple_selection=True,
                        width=80,
                        height=90,
                        font=(tkFont.nametofont("TkDefaultFont"), 10),
                    )
                    self.listbox.grid(
                        row=row,
                        column=1,
                        padx=self.padx,
                        pady=self.pady,
                        sticky=tk.E,
                    )
                    for index, platform in enumerate(self.platform_options):
                        self.listbox.insert(index, platform)
                        if platform in variable:
                            # TODO: not working for more than one value
                            self.listbox.activate(index)

                else:
                    ctk.CTkEntry(self, textvariable=variable).grid(
                        row=row,
                        column=1,
                        sticky=tk.E,
                        padx=self.padx,
                        pady=self.pady,
                    )
        ctk.CTkButton(
            self, text="Save", command=self.write_config, width=600
        ).grid(
            row=row + 1, column=0, columnspan=3, padx=self.padx, pady=self.pady
        )

    def get_values_to_set(self):
        value_dict = {
            "base": {"platforms": self.configuration["base"]["platforms"]}
        }

        value_dict["base"].update(
            {
                key: (tk.StringVar(value=value), type(value))
                for key, value in self.configuration["base"].items()
                if key != "platforms"
            }
        )
        value_dict.update(
            {
                "dship parameters": {
                    key: (tk.StringVar(value=value), type(value))
                    for key, value in self.configuration["dship"][
                        "identifier"
                    ].items()
                }
            }
        )
        return value_dict

    def write_config(self):
        new_base = {}
        for key, value in self.values["base"].items():
            if key != "platforms":
                new_base[key] = value[0].get()
            else:
                new_base[key] = value

        self.configuration["base"] = new_base
        self.configuration["dship"]["identifier"] = {
            key: value[0].get()
            for key, value in self.values["dship parameters"].items()
        }
        self.configuration.write(use_internal_values=False)
        CTkMessagebox(
            title="Info",
            message="You need to restart the application for these settings to have an effect.",
            option_1="Ok",
        )
        # self.configuration.write(use_internal_values=False)
        # self.callbacks["save"]()

    def select_file(self, instrument, name, variable):
        """
        Generic file selection method, that opens a file browsing pop-up.
        """
        if name.endswith("exe"):
            file_type = "exe"
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
        if file:
            variable.set(file)


class AboutView(CtkFrame):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        ctk.CTkLabel(
            self,
            text="This is the CTD-Client developed at the IOW for the DAM. Its purpos...",
        ).grid()


class ContactView(CtkFrame):
    def initialize(self, root):
        super().__init__(master=root)

        ctk.CTkLabel(
            self,
            text="Developed and maintained by Emil Michels, IOW.\nFeel free to contact me in case of problems, if you find a bug or just have a great idea on how to improve this software.\nwebsite: https://www.io-warnemuende.de/emil-michels-en.html\nemail: emil.michels@io-warnemuende.de\ntelephone: +49 381 5197 159",
            justify="left",
        ).grid()
