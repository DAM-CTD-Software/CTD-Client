from ctdclient.controller.Controller import Controller
from ctdclient.model.processing import ProcessingConfig, ProcessingList
from ctdclient.view.processing import ProcessingView


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
        self.view.add_callback("toggle_active", self.toggle_active_state)
        self.update()

    def update(self):
        self.model.read_processing_files()
        self.view.populate(self.model.data)

    def add_new_processing(self):
        return self.model.get_template()

    def delete(self, processing_workflow: ProcessingConfig):
        self.model.remove_config(processing_workflow)
        self.view.populate(self.model.data)

    def toggle_active_state(self, processing_workflow: ProcessingConfig):
        self.model.toggle_config_activity_state(processing_workflow)
