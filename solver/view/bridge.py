import tkinter as tk
import typing
from solver import messaging
from . import state


class EventBridge:

    _TIMEOUT = 50

    def __init__(self, app: tk.Tk, on_message: typing.Callable[[messaging.Message], None]):
        self._app = app
        self._on_message = on_message
        self._buffer: list[messaging.Message] = []

    def message_handler(self, message: messaging.Message) -> None:
        self._buffer.append(message)

    def start(self) -> None:
        self._app.after(self._TIMEOUT, self._timeout_cb)
    
    def _timeout_cb(self) -> None:
        while len(self._buffer) > 0:
            self._on_message(self._buffer.pop(0))
        
        self._app.after(self._TIMEOUT, self._timeout_cb)


class ViewStateMessageHandler:

    def __init__(self, view_state: state.ViewState):
        self._state = view_state

    def handle_message(self, message: messaging.Message) -> None:
        if isinstance(message, messaging.UpdateHLine):
            self._handle_update_hline(message)
        elif isinstance(message, messaging.UpdateVLine):
            self._handle_update_vline(message)

    def _handle_update_hline(self, message: messaging.UpdateHLine) -> None:
        self._state.puzzle_state.set_hline(message.x, message.y, message.state)
        self._state.rerender_hline(message.x, message.y)

    def _handle_update_vline(self, message: messaging.UpdateVLine) -> None:
        self._state.puzzle_state.set_vline(message.x, message.y, message.state)
        self._state.rerender_vline(message.x, message.y)
