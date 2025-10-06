import logging

import customtkinter as ctk
from ctdclient.view.ctkframe import CtkFrame
from CTkMessagebox import CTkMessagebox

logger = logging.getLogger(__name__)


class TabView(ctk.CTkTabview):
    """Collection of multiple windows within one frame, reachable by tabs."""

    def __init__(
        self,
        window: ctk.CTkFrame,
        tabs: dict[str, CtkFrame],
        *args,
        **kwargs,
    ):
        super().__init__(window, *args, **kwargs)
        self.grid()

        for name, view in tabs.items():
            self.add(name)
            self.initialize_views(name, view)
        self.configure(command=self.on_tab_change)

    def initialize_views(self, name, view):
        tab = self.tab(name)
        view.initialize(tab)
        view.grid()

    def on_tab_change(self):
        if "expert" in self.get():
            CTkMessagebox(
                title="Caution",
                message="These settings can break the application, proceed with caution and only if you know what you are doing.",
                option_1="Ok",
            )
