from typing import Callable


class ViewMixin:
    """
    This Mixin provides the link between Views and Controllers without the need
    of View Objects to hold Controller Objects and thereby fullfil
    encapsulation as specified in MVC.
    """

    def __init__(self):
        self.callbacks = {}

    def add_callback(self, key: str, method: Callable):
        """
        Lets tkinter commands directly call a controller method, without
        owning the respective object. This method is exclusevely being used by
        the controller and allows the registration of a certain method to a
        certain keyword, upon which it will be called.
        """

        self.callbacks[key] = method

    def bind_commands_to_callbacks(self, callback: str):
        """
        Allows the usage of callback functions inside of tkinter object that
        feature a command argument.
        """

        return self.callbacks[callback]
