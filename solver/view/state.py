import enum
import typing
from solver import messaging, model


class ViewMode(enum.Enum):
    EDITING = 1
    SOLVING = 2


class ViewState:

    def __init__(self, puzzle_state: model.PuzzleState, publisher: messaging.Publisher):
        self._puzzle_state = puzzle_state
        self._publisher = publisher
        self._rerender_all_handler: typing.Optional[typing.Callable[[], None]] = None
        self._rerender_puzzle_handler: typing.Optional[typing.Callable[[], None]] = None
        self._rerender_hline_handler: typing.Optional[
            typing.Callable[[int, int], None]
        ] = None
        self._rerender_vline_handler: typing.Optional[
            typing.Callable[[int, int], None]
        ] = None

        self.view_mode: ViewMode = ViewMode.EDITING
        self.controls_disabled: bool = False

    @property
    def puzzle_state(self) -> model.PuzzleState:
        return self._puzzle_state

    def register_rerender_all_hander(self, handler: typing.Callable[[], None]) -> None:
        self._rerender_all_handler = handler

    def rerender_all(self) -> None:
        assert self._rerender_all_handler is not None
        self._rerender_all_handler()

    def register_rerender_puzzle_handler(
        self, handler: typing.Callable[[], None]
    ) -> None:
        self._rerender_puzzle_handler = handler

    def rerender_puzzle(self) -> None:
        assert self._rerender_puzzle_handler is not None
        self._rerender_puzzle_handler()

    def register_rerender_hline(
        self, handler: typing.Callable[[int, int], None]
    ) -> None:
        self._rerender_hline_handler = handler

    def rerender_hline(self, x: int, y: int) -> None:
        if self._rerender_hline_handler is not None:
            self._rerender_hline_handler(x, y)

    def register_rerender_vline(
        self, handler: typing.Callable[[int, int], None]
    ) -> None:
        self._rerender_vline_handler = handler

    def rerender_vline(self, x: int, y: int) -> None:
        if self._rerender_vline_handler is not None:
            self._rerender_vline_handler(x, y)
