import customtkinter as ctk
from code_tools.logging import get_logger
from ctdclient.view.ctkframe import CtkFrame
from CTkMessagebox import CTkMessagebox

logger = get_logger(__name__)


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
            self.reparent_to_tab(view, name)
        self.configure(command=self.on_tab_change)

    def reparent_to_tab(self, view, tab_name):
        """Move a view's widgets to a specific tab."""
        tab = self.tab(tab_name)
        view.master = tab
        view.grid()

    def on_tab_change(self):
        if self.get() == "expert settings":
            CTkMessagebox(
                title="Caution",
                message="These settings can break the application, proceed with caution and only if you know what you are doing.",
                option_1="Ok",
            )
