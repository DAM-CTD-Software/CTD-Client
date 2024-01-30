from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import customtkinter as ctk
import json
from functools import partial
import difflib

from mig.backend.configurationhandler import ConfigurationFile
from mig.backend.dshipcaller import DSHIPHeader
from mig.backend.processing import BatchProcessing
from mig.backend.runseasave import RunSeasave


class MainWindow:
    """Top window that encapsulates all other frames."""

    def __init__(self, controller, root, config_path, dship_info, bottles):
        root.title("DAM CTD Software")
        # avoids old 'tear-off' menus
        root.option_add('*tearOff', tk.FALSE)

        # allow window resizing
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # initialize standard menu
        # MenuBar(root)

        # creating tab organisation
        # select one out of NoteBookView, TabView and LabelFrames
        tabs = TabView(root)
        tabs.grid()
        # building individual pages in their own classes
        self.measurement = Measurement(
            tabs.measurement, config_path, bottles, dship_info, controller)
        Processing(tabs.processing, config_path)
        Configuration(tabs.configuration, config_path)
        tabs.measurement.grid()
        tabs.processing.grid()
        tabs.configuration.grid()


class NoteBookView(ttk.Notebook):
    """Basic tkinter equivalent to customtkinter's TabView."""

    def __init__(self, window):
        super().__init__(window)

        self.measurement = ctk.CTkFrame(self)
        self.processing = ctk.CTkFrame(self)
        self.configuration = ctk.CTkFrame(self)
        self.add(self.measurement, text='measurement')
        self.add(self.processing, text='processing')
        self.add(self.configuration, text='configuration')


class TabView(ctk.CTkTabview):
    """Collection of multiple windows within one frame, reachable by tabs. """

    def __init__(self, window, **kwargs):
        super().__init__(window, **kwargs)

        self.add('measurement')
        self.add('processing')
        self.add('configuration')
        self.measurement = ttk.Frame(self.tab('measurement'))
        self.processing = ttk.Frame(self.tab('processing'))
        self.configuration = ttk.Frame(self.tab('configuration'))


class LabelFrames(ttk.PanedWindow):
    """
    Displaying multiple windows next to each other, separated inside boxes.
    """

    def __init__(self, window, **kwargs):
        super().__init__(window, orient=tk.HORIZONTAL, ** kwargs)
        self.measurement = ttk.Labelframe(self, text='measurement')
        self.processing = ttk.Labelframe(self, text='processing')
        self.configuration = ttk.Labelframe(self, text='configuration')
        self.add(self.measurement)
        self.add(self.processing)
        self.add(self.configuration)


class MenuBar:
    """Menu bar that allows some basic configuration."""

    def __init__(self, window) -> None:
        # TODO: implement
        menubar = tk.Menu(window)
        window['menu'] = menubar
        menu_file = tk.Menu(menubar)
        menu_edit = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menubar.add_cascade(menu=menu_edit, label='Edit')


class Measurement:
    """
    A frame that displays the information needed for the CTD measurement,
    DSHIP live data, bottle closing depths and operator and allows to run
    the Seasave software with command line arguments.
    """

    def __init__(self, window, config, bottles, dship_info, controller) -> None:
        self.config = config
        self.bottles = bottles
        self.dship_info = dship_info
        self.controller = controller
        self.dship_values = dship_info.dship_values
        self.dship_vars = {key: tk.StringVar(value=value)
                           for key, value in self.dship_values.items()}
        self.save_btl_config = tk.BooleanVar(value=False)

        self.dship_frame(window)
        self.bottle_frame(window)
        self.run_frame(window)
        window.grid()

    def update_dship_values(self, list_of_values):
        """

        Parameters
        ----------
        list_of_values :


        Returns
        -------

        """
        for ((_, var), value) in zip(self.dship_vars.items(), list_of_values):
            var.set(value)

    def dship_frame(self, window):
        """
        Frame that displays our metadata header information with live-fetched
        DSHIP data. Additionally features a selection field for the current
        operators name, as this is the only header information that can not be
        retrieved from DSHIP.

        Parameters
        ----------
        window :


        Returns
        -------

        """
        # show live dhsip values
        dship_frame = ttk.Frame(window)
        self.dship_label = tk.Label(
            dship_frame,
            text='waiting for connection...',
            background='yellow'
        )
        self.dship_label.grid(row=0, column=0)
        tk.Button(dship_frame, text='Reconnect',
                  command=self.reconnect_dship).grid(row=0, column=1)

        for index, (key, value) in enumerate(self.dship_vars.items()):
            index = index if index < 4 else index+1
            tk.Label(dship_frame, text=key).grid(row=index+1, column=0)
            tk.Label(dship_frame, textvariable=value).grid(
                row=index+1, column=1)

        tk.Label(dship_frame, text='Operator').grid(row=5, column=0)
        self.operator = tk.StringVar(value=self.config['operators']['last'])
        ttk.Combobox(
            dship_frame,
            values=list(self.config['operators'].values())[:-1],
            textvariable=self.operator
        ).grid(row=5, column=1)
        dship_frame.grid(row=0, column=0)

    def bottle_frame(self, window):
        """
        Frame to allow setting the bottle closing depths.

        Parameters
        ----------
        window :


        Returns
        -------

        """
        # configure bottle closing times
        bottle_frame = ttk.Frame(window)
        self.bottle_values = {}
        tk.Label(bottle_frame, text='BottleIDs').grid(column=0, row=0)
        tk.Label(bottle_frame, text='Depth to close').grid(row=0, column=1)
        for index, (key, value) in enumerate(self.bottles.items()):
            textvariable = tk.StringVar()
            textvariable.set(value)
            self.bottle_values[key] = textvariable
            tk.Label(bottle_frame, text=key).grid(row=index+1, column=0)
            tk.Entry(bottle_frame, textvariable=textvariable,
                     justify='center').grid(row=index+1, column=1)
        ttk.Checkbutton(bottle_frame,
                        text='Save Bottle Configuration',
                        variable=self.save_btl_config).grid(column=1)
        bottle_frame.grid(row=0, column=1)

    def run_frame(self, window):
        """
        Frame that wraps the seasave.exe start button with two checkboxes for
        the command line options.

        Parameters
        ----------
        window :


        Returns
        -------

        """
        # start measurement
        run_frame = ttk.Frame(window)
        self.autostart = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            run_frame,
            text='autostart',
            variable=self.autostart,
        ).grid()
        self.downcast = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            run_frame,
            text='downcast',
            variable=self.downcast,
        ).grid()
        tk.Button(run_frame,
                  text='Start Seasave',
                  command=self.start_seasave,
                  ).grid()
        run_frame.grid(row=2, column=1)

    def start_seasave(self):
        """
        Method that is called upon clicking 'Start Seasave'. Organizes
        the information flow of bottle closing information and dship metadata.
        """
        # TODO: handle exceptions
        new_bottle_dict = {key: float(value.get())
                           for key, value in self.bottle_values.items()}
        self.bottles.update_bottle_information(
            new_bottle_dict, self.save_btl_config)
        self.dship_info.build_metadata_header(self.operator.get())
        RunSeasave(self.config).run(self.downcast.get(), self.autostart.get())

    def reconnect_dship(self):
        """"""
        self.controller.reconnect_dship()

    def set_dship_status_good(self):
        """"""
        self.dship_label['background'] = 'green'
        self.dship_label['text'] = 'Live DSHIP values:'

    def set_dship_status_bad(self):
        """"""
        self.dship_label['background'] = 'red'
        self.dship_label['text'] = 'No DSHIP connection'


class Processing:
    """
    A frame to wrap all information and functionality for data processing.
    Is divided in two main parts, the configuration of input paths, to xmlcon,
    hex and psa folder, and the selection of processing modules and their
    respective psas.
    """

    def __init__(self, window, config) -> None:
        self.psa_modules = ['AlignCTD', 'AirPressure', 'BinAvg', 'BottleSum', 'CellTM',
                            'DatCnv', 'Derive', 'Filter', 'LoopEdit', 'WildEdit', 'W_Filter']
        self.config = config
        self.path_dict = {
            'xmlcon': tk.StringVar(value=config['user']['paths']['xmlcon']),
            'hex': tk.StringVar(value=config['user']['paths']['hex']),
            'psa': tk.StringVar(value=config['user']['processing']['psas'])}

        # generate path selection fields
        path_frame = tk.Frame(window)
        for file_type, variable in self.path_dict.items():
            # individual frame construction
            single_frame = tk.Frame(path_frame)
            tk.Label(single_frame, text=f'Path to {file_type}').grid()
            tk.Entry(single_frame, textvariable=variable).grid()
            command_with_arguments = partial(
                self.select_file, file_type, Path(variable.get()))
            tk.Button(single_frame, text='Browse',
                      command=command_with_arguments).grid()
            single_frame.grid()
        path_frame.grid()

        # generate processing selection frame
        self.psa_paths = [path.name for path in Path(
            self.config['user']['processing']['psas']).iterdir()]
        self.steps = self.config['user']['processing']['modules']
        self.step_number = 1
        self.step_var_dict = {}
        modules_frame = tk.Frame(window)
        for user_defined_step in self.steps:
            self.add_processing_step(modules_frame, user_defined_step)
        modules_frame.grid()

        button_frame = tk.Frame(window)
        add_step = partial(self.add_processing_step, modules_frame)
        ttk.Button(
            button_frame,
            text='Add processing step',
            command=add_step
        ).grid(row=0, column=0)
        remove_step = partial(self.remove_processing_step, modules_frame)
        ttk.Button(
            button_frame,
            text='Remove processing step',
            command=remove_step
        ).grid(row=0, column=1)
        button_frame.grid()

        # run processing button
        tk.Button(
            window,
            text='Run processing',
            command=self.run_processing
        ).grid()

    def add_processing_step(self, window, preset_value=''):
        """
        Handles the processing step selection procedure.
        Automatically selects the closest named psa inside of the psa folder.

        Parameters
        ----------
        window : Parent frame

        preset_value : sets the name of the processing step, if already known
             (Default value = '')

        Returns
        -------

        """
        new_step = tk.Frame(window)
        step = tk.StringVar(value=preset_value)

        def psa_default_value(step_value):
            """
            Scans the psa folder for the closest string compared to the step.
            """
            try:
                psa_default_value = difflib.get_close_matches(
                    step_value, self.psa_paths, n=1)[0]
            except IndexError:
                psa_default_value = ''
            return psa_default_value

        def update_psa_value(comboboxObject):
            """Automatically updates the corresponding psa value upon selecting
            a processing step."""
            frame = comboboxObject.widget.master
            psa_box_object = frame.winfo_children()[-1]
            psa_box_object.set(psa_default_value(
                comboboxObject.widget.get()))

        psa = tk.StringVar(value=psa_default_value(preset_value))
        self.step_var_dict[self.step_number] = (step, psa)

        step_box = ttk.Combobox(
            new_step,
            values=self.psa_modules,
            textvariable=step
        )
        step_box.set(preset_value)
        step_box.grid(row=0, column=0)
        step_box.bind('<<ComboboxSelected>>', update_psa_value)
        psa_box = ttk.Combobox(
            new_step,
            values=self.psa_paths,
            textvariable=psa
        )
        psa_box.grid(row=0, column=1)
        new_step.grid()
        self.step_number += 1

    def remove_processing_step(self, frame):
        """
        Handles all the steps needed to remove a processing step from the
        selection frame without leaving any code artifacts behind.
        """
        last_element = frame.winfo_children()[-1]
        last_element.grid_forget()
        last_element.destroy()
        self.step_var_dict.pop(self.step_number-1)
        self.step_number -= 1

    def run_processing(self):
        """Collects the processing step information and feeds it into the
        batch processing routine."""
        info_dict = {key.get(): value.get()
                     for _, (key, value) in self.step_var_dict.items()}
        batch_processing = BatchProcessing(self.config, info_dict)
        batch_processing.run()

    def select_file(self, file_type, path):
        """
        Generic file selection method, that opens a file browsing pop-up.
        """
        filetypes = (
            (f'{file_type} files', f'*.{file_type}'),
            ('All files', '*.*')
        )

        fd.askopenfilename(
            title=f'Path to {file_type}',
            initialdir=path,
            filetypes=filetypes)


class Configuration:
    """ """
    # TODO: implement

    def __init__(self, window, master_config) -> None:
        self.master_config = master_config
        ttk.Button(window, text='Open configuration file',
                   command=self.read_config('')).grid()

    def read_config(self, file_path):
        """

        Parameters
        ----------
        file_path :


        Returns
        -------

        """
        try:
            with open(file_path, 'r') as file:
                config_data = json.load(file)
            return config_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading config file: {e}")
            return {}

    def save_config(self, file_path, config_data):
        """

        Parameters
        ----------
        file_path :

        config_data :


        Returns
        -------

        """
        try:
            with open(file_path, 'w') as file:
                json.dump(config_data, file, indent=4)
            print("Config saved successfully.")
        except Exception as e:
            print(f"Error saving config file: {e}")


if __name__ == "__main__":
    # main application when not called from inside the controller
    root = ctk.CTk()
    import platform
    import sys
    if platform.system() == 'Linux':
        config_path = 'master_config.toml'
    elif platform.system() == 'Windows':
        file_location = Path(__file__).parents[3]
        config_path = file_location.joinpath('windows_config.toml')
    else:
        sys.exit(1)
    config = ConfigurationFile(config_path)
    dship_info = DSHIPHeader(config)
    MainWindow(root, config, dship_info)
    # fullscreen option:
    # root.after(0, lambda: root.state('zoomed'))
    root.mainloop()
    dship_info.end_listener()
