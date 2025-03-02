from dataclasses import dataclass
import enum
import typing
from solver import model


SolverPosition = typing.Tuple[int, int]


class LineDirection(enum.Enum):
    HORIZONTAL = 1
    VERTICAL = 2


class GuessPriority:
    PARTIAL_CORNER = 5
    UNKNOWN_RESTRICTIVE_TILE = 3
    PARTIAL_ANY_TILE = 1
    REMAINING = 0


@dataclass(frozen=True)
class GuessCandidate:
    direction: LineDirection
    x: int
    y: int


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
    def may_place_line_up(self) -> bool:
        return self.line_up is not None and self.line_up != model.LineState.EMPTY

    @property
    def may_place_line_down(self) -> bool:
        return self.line_down is not None and self.line_down != model.LineState.EMPTY

    @property
    def may_place_line_left(self) -> bool:
        return self.line_left is not None and self.line_left != model.LineState.EMPTY

    @property
    def may_place_line_right(self) -> bool:
        return self.line_right is not None and self.line_right != model.LineState.EMPTY

    @property
    def count_lines(self) -> int:
        return self._count_adjacent_edges(model.LineState.LINE)

    @property
    def count_any(self) -> int:
        return self._count_adjacent_edges(model.LineState.ANY)

    @property
    def is_filled(self) -> bool:
        return self.count_any == 0

    def _count_adjacent_edges(self, state: model.LineState) -> int:
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

    @property
    def is_corner(self) -> bool:
        if self.count_lines != 2:
            return False

        return (self.line_up == model.LineState.LINE) != (
            self.line_down == model.LineState.LINE
        )

    @property
    def may_be_corner(self) -> bool:
        if self.is_straight:
            return False
        may_horizontal = self.may_place_line_left or self.may_place_line_right
        may_vertical = self.may_place_line_up or self.may_place_line_down
        return may_horizontal and may_vertical

    @property
    def is_straight(self) -> bool:
        if self.count_lines != 2:
            return False

        return (self.line_up == model.LineState.LINE) == (
            self.line_down == model.LineState.LINE
        )

    @property
    def may_be_straight(self) -> bool:
        if self.is_corner:
            return False
        may_horizontal = self.may_place_line_left and self.may_place_line_right
        may_vertical = self.may_place_line_up and self.may_place_line_down
        return may_horizontal or may_vertical

    @property
    def adjacent_vertex_up(self) -> typing.Optional["Vertex"]:
        return (
            Vertex(puzzle_state=self._puzzle_state, x=self.x, y=self.y - 1)
            if self._puzzle_state.get_tile(self.x, self.y - 1) is not None
            else None
        )

    @property
    def adjacent_vertex_down(self) -> typing.Optional["Vertex"]:
        return (
            Vertex(puzzle_state=self._puzzle_state, x=self.x, y=self.y + 1)
            if self._puzzle_state.get_tile(self.x, self.y + 1) is not None
            else None
        )

    @property
    def adjacent_vertex_left(self) -> typing.Optional["Vertex"]:
        return (
            Vertex(puzzle_state=self._puzzle_state, x=self.x - 1, y=self.y)
            if self._puzzle_state.get_tile(self.x - 1, self.y) is not None
            else None
        )

    @property
    def adjacent_vertex_right(self) -> typing.Optional["Vertex"]:
        return (
            Vertex(puzzle_state=self._puzzle_state, x=self.x + 1, y=self.y)
            if self._puzzle_state.get_tile(self.x + 1, self.y) is not None
            else None
        )

    @property
    def adjacent_vertices(self) -> list["Vertex"]:
        adjacent = [
            self.adjacent_vertex_up,
            self.adjacent_vertex_down,
            self.adjacent_vertex_left,
            self.adjacent_vertex_right,
        ]

        return [a for a in adjacent if a is not None]


class AffectedPositions:

    def __init__(self, puzzle_state: model.PuzzleState):
        self._puzzle_state = puzzle_state

    def tiles_for_hline(self, x: int, y: int) -> set[SolverPosition]:
        return self._tile_and_adjacent(x, y).union(self._tile_and_adjacent(x + 1, y))

    def tiles_for_vline(self, x: int, y: int) -> set[SolverPosition]:
        return self._tile_and_adjacent(x, y).union(self._tile_and_adjacent(x, y + 1))

    def _tile_and_adjacent(self, x: int, y: int, prevent_recurse: bool=False) -> set[SolverPosition]:
        affected: set[SolverPosition] = {(x, y)}
        vertex = Vertex(puzzle_state=self._puzzle_state, x=x, y=y)
        for adjacent in vertex.adjacent_vertices:
            affected.add((adjacent.x, adjacent.y))
            if adjacent.type == model.TileType.STRAIGHT and not prevent_recurse:
                affected.update(self._tile_and_adjacent(adjacent.x, adjacent.y, prevent_recurse=True))
        
        return affected
