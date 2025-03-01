import abc
import typing
from . import event


class Publisher(abc.ABC):

    @abc.abstractmethod
    def send(self, message: event.Message) -> None:
        pass


class MessageBus(Publisher):

    def __init__(self) -> None:
        self._handlers: list[typing.Callable[[event.Message], None]] = []

    def subscribe(self, handler: typing.Callable[[event.Message], None]) -> None:
        self._handlers.append(handler)

    def send(self, message: event.Message) -> None:
        for handler in self._handlers:
            handler(message)
