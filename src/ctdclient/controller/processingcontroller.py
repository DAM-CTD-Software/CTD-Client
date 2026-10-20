import shutil
import subprocess
import sys
from pathlib import Path

from ctdclient.controller.Controller import Controller
from ctdclient.definitions import CONFIG_PATH, PROCESSING_TEMPLATE_PATH
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
        self.view.add_callback("edit_processing", self.edit_processing)
        self.view.add_callback("update_processing_workflows", self.update)
        self.view.add_callback("delete_processing", self.delete)
        self.view.add_callback("toggle_active", self.toggle_active_state)
        self.view.add_callback("update_auto_process", self.update_auto_process)
        self.update()

    def update_auto_process(self, auto_process: str):
        self.model.toggle_auto_process(bool(auto_process))

    def update(self):
        self.model.read_processing_files()
        self.view.populate(self.model.data)

    def add_new_processing(self, name):
        path = CONFIG_PATH / f"processing_{Path(name).stem}.toml"
        if path.exists():
            self.view.error_message("That workflow name already exists.")
            return
        shutil.copyfile(PROCESSING_TEMPLATE_PATH, path)
        workflow = self.model.create_new_processing_config(path)
        self.model.append(workflow)
        self.view.populate(self.model.data)
        self.edit_processing(workflow)

    def edit_processing(self, workflow):
        editor = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "ctdclient.workflow_editor",
                str(workflow.path_to_config),
            ]
        )
        self.wait_for_editor(editor, workflow)

    def wait_for_editor(self, editor, workflow):
        if editor.poll() is None:
            self.view.after(500, self.wait_for_editor, editor, workflow)
        else:
            workflow.update_config(workflow.path_to_config)
            self.view.populate(self.model.data)

    def delete(self, processing_workflow: ProcessingConfig):
        self.model.remove_config(processing_workflow)
        self.view.populate(self.model.data)

    def toggle_active_state(self, processing_workflow: ProcessingConfig):
        self.model.toggle_config_activity_state(processing_workflow)
