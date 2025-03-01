import threading
from solver import algorithm, messaging, model


def start_solver(
    puzzle_state: model.PuzzleState, publisher: messaging.Publisher
) -> None:
    puzzle_copy = _PublishingPuzzle(width=1, height=1, publisher=publisher)
    puzzle_copy.apply(puzzle_state)

    thread = _SolverThread(puzzle_state=puzzle_copy, publisher=publisher)
    thread.start()


class _SolverThread(threading.Thread):

    def __init__(self, puzzle_state: model.PuzzleState, publisher: messaging.Publisher):
        super().__init__()
        self._puzzle = puzzle_state
        self._publisher = publisher

    def run(self) -> None:
        solver = algorithm.Solver(puzzle_state=self._puzzle)
        solver.solve()

        self._publisher.send(messaging.SolverCompleted())


class _PublishingPuzzle(model.PuzzleState):

    def __init__(self, width: int, height: int, publisher: messaging.Publisher) -> None:
        super().__init__(width, height)
        self._publisher = publisher

    def set_hline(self, x: int, y: int, state: model.LineState) -> None:
        super().set_hline(x, y, state)
        self._publisher.send(messaging.UpdateHLine(x=x, y=y, state=state))

    def set_vline(self, x: int, y: int, state: model.LineState) -> None:
        super().set_vline(x, y, state)
        self._publisher.send(messaging.UpdateVLine(x=x, y=y, state=state))
