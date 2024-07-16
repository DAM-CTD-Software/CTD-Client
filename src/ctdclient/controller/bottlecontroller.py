from ctdclient.controller.Controller import Controller
from ctdclient.model.bottles import BottleClosingDepths
from ctdclient.view.bottleframe import BottleFrame


class BottleController(Controller):

    def __init__(
        self,
        *args,
        **kwargs,
    ):

        super().__init__(*args, **kwargs)
        self.model: BottleClosingDepths
        self.view: BottleFrame
        self.initialize()

    def initialize(self):
        self.initialize_bottle_setup()

    def initialize_bottle_setup(self):
        self.view.initialize(self.model)
