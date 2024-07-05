from typing import Callable


class Controller:

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def register_callback(self, key: str, method: Callable):
        self.view.add_callback(key, method)
