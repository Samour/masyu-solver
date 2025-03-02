import time
import threading
from solver import algorithm, messaging, model


_DELAY = 0.1


def start_solver(
    puzzle_state: model.PuzzleState, publisher: messaging.Publisher
) -> None:
    puzzle_copy = _PublishingPuzzle(width=1, height=1, publisher=publisher)
    puzzle_copy.apply(puzzle_state)

    thread = _SolverThread(puzzle_state=puzzle_copy, publisher=publisher)
    thread.start()


class _PublishingPuzzle(model.PuzzleState):

    def __init__(self, width: int, height: int, publisher: messaging.Publisher) -> None:
        super().__init__(width, height)
        self.publishing: bool = False
        self.delay: bool = False
        self._publisher = publisher

    def set_hline(self, x: int, y: int, state: model.LineState) -> None:
        super().set_hline(x, y, state)

        if self.publishing:
            self._publisher.send(messaging.UpdateHLine(x=x, y=y, state=state))
            self._delay()

    def set_vline(self, x: int, y: int, state: model.LineState) -> None:
        super().set_vline(x, y, state)

        if self.publishing:
            self._publisher.send(messaging.UpdateVLine(x=x, y=y, state=state))
            self._delay()

    def apply(self, state: model.PuzzleState) -> None:
        self.delay = False
        super().apply(state)
        self.delay = True

    def _delay(self) -> None:
        if self.delay and _DELAY > 0:
            time.sleep(_DELAY)


class _SolverThread(threading.Thread):

    def __init__(self, puzzle_state: _PublishingPuzzle, publisher: messaging.Publisher):
        super().__init__()
        self._puzzle = puzzle_state
        self._publisher = publisher

    def run(self) -> None:
        self._puzzle.publishing = True
        self._puzzle.delay = True
        solver = algorithm.Solver(puzzle_state=self._puzzle)
        solver.solve()

        self._publisher.send(messaging.SolverCompleted())
