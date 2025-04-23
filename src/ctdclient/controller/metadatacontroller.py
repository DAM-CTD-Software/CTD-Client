from ctdclient.controller.Controller import Controller
from ctdclient.model.metadataheader import MetadataHeader
from ctdclient.view.infoframe import InfoFrame


class MetadataController(Controller):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.model: MetadataHeader
        self.view: InfoFrame
