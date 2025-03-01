import abc
import typing
from solver import model
from . import positions


class Vertex:

    def __init__(self, puzzle_state: model.PuzzleState, x: int, y: int):
        self._puzzle_state = puzzle_state
        self.x = x
        self.y = y

    @property
    def type(self) -> model.TileType:
        tile = self._puzzle_state.get_tile(self.x, self.y)
        assert tile is not None
        return tile

    @property
    def line_up(self) -> typing.Optional[model.LineState]:
        return self._puzzle_state.get_vline(self.x, self.y - 1)

    @property
    def line_down(self) -> typing.Optional[model.LineState]:
        return self._puzzle_state.get_vline(self.x, self.y)

    @property
    def line_left(self) -> typing.Optional[model.LineState]:
        return self._puzzle_state.get_hline(self.x - 1, self.y)

    @property
    def line_right(self) -> typing.Optional[model.LineState]:
        return self._puzzle_state.get_hline(self.x, self.y)

    @property
    def count_lines(self) -> int:
        return self._count_adjacent(model.LineState.LINE)

    @property
    def count_any(self) -> int:
        return self._count_adjacent(model.LineState.ANY)

    @property
    def is_filled(self) -> bool:
        return self.count_any == 0

    def _count_adjacent(self, state: model.LineState) -> int:
        lines = 0
        if self.line_up == state:
            lines += 1
        if self.line_down == state:
            lines += 1
        if self.line_left == state:
            lines += 1
        if self.line_right == state:
            lines += 1
        return lines


class VertexSolver(abc.ABC):

    def __init__(self, puzzle_state: model.PuzzleState):
        self.puzzle_state = puzzle_state

    @abc.abstractmethod
    def make_updates(self, vertex: Vertex) -> set[positions.SolverPosition]:
        pass


class FillEmptyEdgesVS(VertexSolver):

    def make_updates(self, vertex: Vertex) -> set[positions.SolverPosition]:
        if vertex.count_lines != 2:
            return set()

        updates: set[positions.SolverPosition] = set()
        if vertex.line_up == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y - 1, model.LineState.EMPTY)
            updates.update(positions.tiles_for_vline(vertex.x, vertex.y - 1))
        if vertex.line_down == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y, model.LineState.EMPTY)
            updates.update(positions.tiles_for_vline(vertex.x, vertex.y))
        if vertex.line_left == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x - 1, vertex.y, model.LineState.EMPTY)
            updates.update(positions.tiles_for_hline(vertex.x - 1, vertex.y))
        if vertex.line_right == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x, vertex.y, model.LineState.EMPTY)
            updates.update(positions.tiles_for_hline(vertex.x, vertex.y))

        return updates


class DeadEndVS(VertexSolver):

    def make_updates(self, vertex: Vertex) -> set[positions.SolverPosition]:
        if vertex.count_any != 1:
            return set()

        if vertex.line_up == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y - 1, model.LineState.EMPTY)
            return positions.tiles_for_vline(vertex.x, vertex.y - 1)
        elif vertex.line_down == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y, model.LineState.EMPTY)
            return positions.tiles_for_vline(vertex.x, vertex.y)
        elif vertex.line_left == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x - 1, vertex.y, model.LineState.EMPTY)
            return positions.tiles_for_hline(vertex.x - 1, vertex.y)
        elif vertex.line_right == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x, vertex.y, model.LineState.EMPTY)
            return positions.tiles_for_hline(vertex.x, vertex.y)

        return set()


class OnlyLineOptionVS(VertexSolver):

    def make_updates(self, vertex: Vertex) -> set[positions.SolverPosition]:
        if vertex.count_lines != 1 or vertex.count_any != 1:
            return set()

        if vertex.line_up == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y - 1, model.LineState.LINE)
            return positions.tiles_for_vline(vertex.x, vertex.y - 1)
        elif vertex.line_down == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y, model.LineState.LINE)
            return positions.tiles_for_vline(vertex.x, vertex.y)
        elif vertex.line_left == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x - 1, vertex.y, model.LineState.LINE)
            return positions.tiles_for_hline(vertex.x - 1, vertex.y)
        elif vertex.line_right == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x, vertex.y, model.LineState.LINE)
            return positions.tiles_for_hline(vertex.x, vertex.y)

        return set()
