import logging
import time
from typing import Any, Protocol

logging.basicConfig(level=logging.DEBUG)


class Activity(Protocol):
    # Base activity methods
    def interact(self, event) -> bool:
        ...
    
    def render(self, timestamp: float, screen) -> bool:
        ...

    # Events
    # def on_leave(self):
    #     pass

    # def on_exit(self):
    #     pass

    # def on_return(self, value):
    #     pass


class GameLoop:
    REGISTER = {}

    @classmethod
    def register(cls, name):
        def wrapper(klass):
            assert name not in cls.REGISTER, f"Activity {name} already registered!"
            assert isinstance(klass, Activity)
            logging.info('Registered %s Activity with %s', name, klass)
            cls.REGISTER[name] = klass
            return klass

        return wrapper

    def __init__(self):
        self.stack = []

    def enter(self, name: str, **kwargs):
        assert name in self.REGISTER, f"Activity {name} not registered!"

        klass = self.REGISTER[name]

        if self.stack and hasattr(self.stack[-1], 'on_leave'):
            self.stack[-1].on_leave()

        activity = klass(**kwargs)
        activity.loop = self
        self.stack.append(activity)

    def switch(self, name: str, **kwargs):
        # TODO: assert caller 
        assert name in self.REGISTER, f"Activity {name} not registered!"
        klass = self.REGISTER[name]

        assert self.stack
        activity = self.stack.pop()
        if hasattr(activity, 'on_exit'):
            activity.on_exit()

        activity = klass(**kwargs)
        activity.loop = self
        self.stack.append(activity)

    def exit(self, retvalue: Any = None, **retvalues):
        # TODO: assert caller
        if retvalues:
            assert retvalue is None
            retvalue = retvalues

        assert self.stack
        activity = self.stack.pop()
        if hasattr(activity, 'on_exit'):
            activity.on_exit()

        if self.stack and hasattr(self.stack[-1], 'on_return'):
            self.stack[-1].on_return(retvalue)

    #######
    def interact(self, event) -> bool:
        return self.stack[-1].interact(event)

    def render(self, timestamp, screen) -> bool:
        return self.stack[-1].render(timestamp, screen)

    def wait(self, fps):
        time.sleep(1.0 / fps)


