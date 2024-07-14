import tkinter as tk

from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.procstep import ProcessingStep
from ctdclient.view.View import ViewMixin


class ProcessingStepFrame(ViewMixin, CtkFrame):
    """
    Frame to hold the dynamic drop-downs for processing step and psa
    selection.
    """

    def __init__(
        self,
        *args,
        steps: list[tuple] = [],
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.steps = [
            (tk.StringVar(value=step), tk.StringVar(value=psa))
            for (step, psa) in steps
        ]
        print(steps)
        self.step_options = []
        self.psa_paths = []
        self.load_steps()

    def load_steps(self):
        for child in self.winfo_children():
            child.kill()
        for step, psa in self.steps:
            step_frame = ProcessingStep(
                self, configuration=self.configuration, step=step, psa=psa
            )
            step_frame.grid()
        self.grid()
        self.steps = [
            (child.step, child.psa) for child in self.winfo_children()
        ]
        print(self.winfo_children)

    def add_step(self, child_object: ProcessingStep):
        index = self.steps.index((child_object.step, child_object.psa))
        self.steps.insert(
            index,
            (tk.StringVar(value=self.step_options[0]), tk.StringVar(value="")),
        )

    def remove_step(self, child_object: ProcessingStep):
        try:
            self.steps.remove((child_object.step, child_object.psa))
        except ValueError:
            child_object.kill()
            self.load_steps()

    def get_children(self) -> list:
        return self.winfo_children()

    def tuple_list_to_step_dict(self) -> dict[str, dict]:
        try:
            info_dict = {
                key.get(): ({"psa": value.get()} if value.get() != "" else {})
                for (key, value) in self.steps
            }
        except AttributeError:
            info_dict = {}
        return info_dict
