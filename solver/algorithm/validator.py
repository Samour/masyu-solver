import enum
import typing
from solver import model


class _LineDirection(enum.Enum):
    HORIZONTAL = 1
    VERTICAL = 2


class _MovementDirection(enum.Enum):
    FORWARD = 1  # Right or down
    BACKWARD = 2  # Left or up


LineSpec = typing.Tuple[_LineDirection, int, int]


class SolutionValidator:

    def __init__(self, puzzle_state: model.PuzzleState):
        self._state = puzzle_state
        self._vertices: set[typing.Tuple[int, int]] = set()
        self._lines: set[LineSpec] = set()
        self._starting_point: typing.Optional[LineSpec] = None
        self._current_position: typing.Optional[LineSpec] = None
        self._direction: _MovementDirection = _MovementDirection.FORWARD

    def is_solved(self) -> bool:
        self._discover_vertices()
        self._discover_lines()
        if self._starting_point is None:
            return False

        self._direction = _MovementDirection.FORWARD
        while True:
            if not self._step():
                return False

            if self._current_position == self._starting_point:
                break

        return len(self._vertices) == 0 and len(self._lines) == 0

    def _discover_vertices(self) -> None:
        self._vertices = set()
        for y in range(self._state.height):
            for x in range(self._state.width):
                if self._state.get_tile(x, y) != model.TileType.ANY:
                    self._vertices.add((x, y))

    def _discover_lines(self) -> None:
        self._starting_point = None
        self._lines = set()
        for y in range(self._state.height):
            for x in range(self._state.width - 1):
                if self._state.get_hline(x, y) == model.LineState.LINE:
                    self._lines.add((_LineDirection.HORIZONTAL, x, y))
                    if self._starting_point is None:
                        self._starting_point = (_LineDirection.HORIZONTAL, x, y)

        for y in range(self._state.height - 1):
            for x in range(self._state.width):
                if self._state.get_vline(x, y) == model.LineState.LINE:
                    self._lines.add((_LineDirection.VERTICAL, x, y))
                    if self._starting_point is None:
                        self._starting_point = (_LineDirection.VERTICAL, x, y)

        self._current_position = self._starting_point

    def _step(self) -> bool:
        assert self._current_position is not None
        next_pos = self._next_position()
        if next_pos is None:
            return False

        _, c_x, c_y = self._current_position
        vertex, (n_d, n_x, n_y) = next_pos
        if not self._validate_vertex(vertex, n_d):
            return False

        self._vertices.discard(vertex)
        self._lines.remove(self._current_position)
        if n_x < c_x or n_y < c_y:
            self._direction = _MovementDirection.BACKWARD
        else:
            self._direction = _MovementDirection.FORWARD
        self._current_position = (n_d, n_x, n_y)

        return True

    def _next_position(
        self,
    ) -> typing.Optional[typing.Tuple[typing.Tuple[int, int], LineSpec]]:
        assert self._current_position is not None
        t_x, t_y = self._next_vertex()
        adjacent_lines = self._enumerate_lines(t_x, t_y)
        adjacent_lines.remove(self._current_position)

        if len(adjacent_lines) != 1:
            return None

        return (t_x, t_y), next(iter(adjacent_lines))

    def _next_vertex(self) -> typing.Tuple[int, int]:
        assert self._current_position is not None
        c_d, c_x, c_y = self._current_position
        x: typing.Optional[int] = None
        y: typing.Optional[int] = None
        if self._direction == _MovementDirection.BACKWARD:
            x = c_x
            y = c_y
        elif self._direction == _MovementDirection.FORWARD:
            if c_d == _LineDirection.HORIZONTAL:
                x = c_x + 1
                y = c_y
            elif c_d == _LineDirection.VERTICAL:
                x = c_x
                y = c_y + 1

        assert x is not None and y is not None
        return x, y

    def _enumerate_lines(self, x: int, y: int) -> set[LineSpec]:
        lines: set[LineSpec] = set()
        if self._state.get_hline(x, y) == model.LineState.LINE:
            lines.add((_LineDirection.HORIZONTAL, x, y))
        if self._state.get_hline(x - 1, y) == model.LineState.LINE:
            lines.add((_LineDirection.HORIZONTAL, x - 1, y))
        if self._state.get_vline(x, y) == model.LineState.LINE:
            lines.add((_LineDirection.VERTICAL, x, y))
        if self._state.get_vline(x, y - 1) == model.LineState.LINE:
            lines.add((_LineDirection.VERTICAL, x, y - 1))

        return lines

    def _validate_vertex(
        self, vertex: typing.Tuple[int, int], next_line_direction: _LineDirection
    ) -> bool:
        # This only considers the immediate vertex right now, not whether there is an adjacent corner or not
        assert self._current_position is not None
        v_x, v_y = vertex
        tile_type = self._state.get_tile(v_x, v_y)
        d, _, _ = self._current_position

        if tile_type == model.TileType.ANY:
            return True
        elif tile_type == model.TileType.STRAIGHT:
            return d == next_line_direction
        elif tile_type == model.TileType.CORNER:
            return d != next_line_direction
        assert False
