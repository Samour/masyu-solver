import enum
import typing
from solver import model


class ViewMode(enum.Enum):
    EDITING = 1
    SOLVING = 2


class ViewState:

    def __init__(self, puzzle_state: model.PuzzleState):
        self._puzzle_state = puzzle_state
        self._rerender_puzzle_handler: typing.Optional[typing.Callable[[], None]] = None

        self.view_mode: ViewMode = ViewMode.EDITING

    @property
    def puzzle_state(self) -> model.PuzzleState:
        return self._puzzle_state

    def register_rerender_puzzle_handler(
        self, handler: typing.Callable[[], None]
    ) -> None:
        self._rerender_puzzle_handler = handler

    def rerender_puzzle(self) -> None:
        assert self._rerender_puzzle_handler is not None
        self._rerender_puzzle_handler()
