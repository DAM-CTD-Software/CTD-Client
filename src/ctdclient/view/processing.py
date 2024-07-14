from ctdclient.view.ctkframe import CtkFrame
from ctdclient.view.headerframe import HeaderFrame
from ctdclient.view.proccustomframe import ProcessingCustomScriptFrame
from ctdclient.view.procstepframe import ProcessingStepFrame


class ProcessingView(CtkFrame):
    """
    A frame to wrap all information and functionality for data processing.
    Is divided in two main parts, the configuration of input paths, to xmlcon,
    hex and psa folder, and the selection of processing modules and their
    respective psas.
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # self.file_path = tk.StringVar(value=self.processing.file_path)

        # layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def populate(self, custom_script: bool, steps: list[tuple] = []):
        if len(self.winfo_children()) > 0:
            for child in self.winfo_children():
                child.kill()
        if custom_script:
            self.steps_frame = ProcessingCustomScriptFrame(
                self, configuration=self.configuration
            )
        else:
            self.steps_header = HeaderFrame(
                self,
                configuration=self.configuration,
                header_text="Processing steps",
            )
            self.steps_frame = ProcessingStepFrame(
                self.steps_header,
                configuration=self.configuration,
                steps=steps,
            )
