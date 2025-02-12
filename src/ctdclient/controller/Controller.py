from typing import Callable

from ctdclient.configurationhandler import ConfigurationFile
from ctdclient.view.View import ViewMixin


class Controller:
    """
    Controller in the spirit of the MVC model.
    Coordinates between the views and models. Holds instances of the root
    window and of every model class. Features methods that correspond to one
    individual user interaction with the GUI.
    """

    def __init__(
        self,
        configuration: ConfigurationFile,
        model,
        view: ViewMixin,
    ):
        self.configuration = configuration
        self.model = model
        self.view = view
        # instance check until all models migrated to using the mixin
        if hasattr(model, "error_callback"):
            self.register_error_message()

    def register_callback(
        self,
        key: str,
        method: Callable,
    ):
        """
        Registers the other controllers methods to their respective actions in
        the view objects. Those can then be called from the views without them
        holding an instance of this class.
        """
        self.view.add_callback(key, method)

    def register_error_message(self):
        self.model.error_callback = self.view.error_message