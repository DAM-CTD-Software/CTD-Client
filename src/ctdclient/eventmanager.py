from typing import Callable


class EventManager:
    """
    Central event manager to handle communication between components, in the
    spirit of the observer pattern.
    """

    def __init__(self):
        self._listeners = {}

    def subscribe(self, event_name: str, callback: Callable):
        """Register a listener for a specific event."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable):
        """Remove a listener for a specific event."""
        if event_name in self._listeners:
            self._listeners[event_name].remove(callback)
            if not self._listeners[event_name]:
                del self._listeners[event_name]

    def publish(self, event_name: str, *args, **kwargs):
        """Notify all listeners of an event."""
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                callback(*args, **kwargs)
