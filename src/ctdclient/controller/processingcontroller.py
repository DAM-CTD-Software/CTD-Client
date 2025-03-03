from pathlib import Path

from ctdclient.controller.Controller import Controller
from ctdclient.model.processing import ProcessingConfig
from ctdclient.model.processing import ProcessingList
from ctdclient.view.processing import ProcessingView
from tomlkit.exceptions import NonExistentKey


class ProcessingController(Controller):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.model: ProcessingList
        self.view: ProcessingView
        self.view.add_callback("new_processing", self.add_new_processing)
        self.view.add_callback("update_processing_workflows", self.update)
        self.view.add_callback("delete_processing", self.delete)
        self.update()

    def update(self):
        self.model.read_processing_files()
        self.view.populate(self.model.data)
        # self.set_config_file_path(file_path)
        # self.reload_view()

    def add_new_processing(self):
        return self.model.get_template()

    def delete(self, processing_workflow: ProcessingConfig):
        self.model.remove_config(processing_workflow)
        self.view.populate(self.model.data)

    # def reload_view(self):
    # initialize view data
    # self.view.populate(self.use_custom_script, self.config_file_path)
    # set callbacks
    # self.view.steps_frame.add_callback("configload", self.load_processing)

    # def set_config_file_path(self, file_path: Path | str):
    #     self.config_file_path = Path(file_path)
    #     self.model.update_config(
    #         self.config_file_path,
    #         self.configuration.generate_processing_fingerprint,
    #         self.configuration.file_type_dir,
    #     )
    #
    # def step_dict_to_tuple_list(self, steps: dict[str, dict]) -> list[tuple]:
    #     tuple_list = []
    #     for step, infos in steps.items():
    #         try:
    #             psa = infos["psa"]
    #         except NonExistentKey:
    #             psa = ""
    #         finally:
    #             tuple_list.append((step, psa))
    #     return tuple_list

    # def update_processing_info(self, general_infos: dict, steps: dict):
    #     processing_dict = {key: value.get()
    #                        for key, value in general_infos.items()}
    #     processing_dict = {
    #         **processing_dict,
    #         "modules": self.tuple_list_to_step_dict(steps),
    #     }
    #     return processing_dict
    #
    # def tuple_list_to_step_dict(self, steps: dict) -> dict:
    #     try:
    #         info_dict = {
    #             key.get(): ({"psa": value.get()} if value.get() != "" else {})
    #             for _, (key, value) in steps.items()
    #         }
    #     except AttributeError:
    #         info_dict = {}
    #     return info_dict
    #
    # def set_psa_selection(self, directory):
    #     """"""
    #     self.psa_paths = [path.name for path in Path(directory).iterdir()]
    #     self.psa_paths = sorted(self.psa_paths, key=str.lower)
