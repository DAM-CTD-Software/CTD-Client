import tkinter as tk
from pathlib import Path

from ctdclient.controller.Controller import Controller
from ctdclient.model.processing import Processing
from ctdclient.view.processing import ProcessingView
from tomlkit.exceptions import NonExistentKey


class ProcessingController(Controller):

    def __init__(
        self,
        *args,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)
        self.model: Processing
        self.view: ProcessingView
        # variables
        self.use_custom_script = False
        self.target_file: Path
        self.load_processing(self.configuration.last_processing_file)

    def reload_view(self):
        # initialize view data
        self.view.populate(self.use_custom_script, [], self.config_file_path)
        # self.view.steps_frame.psa_paths = self.model.psa_paths
        # self.view.steps_frame.step_options = self.model.step_names
        # set callbacks
        self.view.steps_frame.add_callback("configload", self.load_processing)

    def set_config_file_path(self, file_path: Path | str):
        self.config_file_path = Path(file_path)
        self.model.update_config(
            self.config_file_path,
            self.configuration.generate_processing_fingerprint,
        )
        if self.config_file_path.suffix == ".toml":
            self.use_custom_script = True
        else:
            self.use_custom_script = True

    def step_dict_to_tuple_list(self, steps: dict[str, dict]) -> list[tuple]:
        tuple_list = []
        for step, infos in steps.items():
            try:
                psa = infos["psa"]
            except NonExistentKey:
                psa = ""
            finally:
                tuple_list.append((step, psa))
        return tuple_list

    def load_processing(self, file_path: Path | str):
        self.set_config_file_path(file_path)
        self.reload_view()

    def update_processing_info(self, general_infos: dict, steps: dict):
        processing_dict = {
            key: value.get() for key, value in general_infos.items()
        }
        processing_dict = {
            **processing_dict,
            "modules": self.tuple_list_to_step_dict(steps),
        }
        return processing_dict

    def tuple_list_to_step_dict(self, steps: dict) -> dict:
        try:
            info_dict = {
                key.get(): ({"psa": value.get()} if value.get() != "" else {})
                for _, (key, value) in steps.items()
            }
        except AttributeError:
            info_dict = {}
        return info_dict

    def set_psa_selection(self, directory):
        """"""
        self.psa_paths = [path.name for path in Path(directory).iterdir()]
        self.psa_paths = sorted(self.psa_paths, key=str.lower)
