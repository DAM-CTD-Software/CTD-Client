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


class ModelA:
    def __init__(self, event_manager):
        self.event_manager = event_manager

    def do_something(self):
        # Notify listeners about the event
        print("ModelA: Doing something and notifying listeners...")
        self.event_manager.publish("event_happened", data="Hello from ModelA")


class ModelB:
    def __init__(self, event_manager):
        self.event_manager = event_manager
        # Subscribe to the "event_happened" event
        self.event_manager.subscribe("event_happened", self.on_event_happened)

    def on_event_happened(self, data):
        print(f"ModelB: Received event with data: {data}")
