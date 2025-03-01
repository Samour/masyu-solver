import enum
import typing
from solver import model


class SolutionValue(enum.Enum):
    UNSOLVED = 1
    SOLVED = 2
    INVALID = 3


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

    def is_solved(self) -> SolutionValue:
        self._discover_vertices()
        self._discover_lines()
        if self._starting_point is None:
            return SolutionValue.UNSOLVED

        self._direction = _MovementDirection.FORWARD
        while True:
            step_result = self._step()
            if step_result is not None:
                return step_result

            if self._current_position == self._starting_point:
                break

        return (
            SolutionValue.SOLVED
            if len(self._vertices) == 0 and len(self._lines) == 0
            else SolutionValue.INVALID
        )

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

    def _step(self) -> typing.Optional[SolutionValue]:
        assert self._current_position is not None
        next_pos = self._next_position()
        if next_pos is None:
            return SolutionValue.UNSOLVED

        _, c_x, c_y = self._current_position
        (v_x, v_y), (n_d, n_x, n_y) = next_pos
        if not self._validate_vertex(v_x, v_y):
            return SolutionValue.INVALID

        self._vertices.discard((v_x, v_y))
        self._lines.remove(self._current_position)
        if n_x < c_x or n_y < c_y:
            self._direction = _MovementDirection.BACKWARD
        else:
            self._direction = _MovementDirection.FORWARD
        self._current_position = (n_d, n_x, n_y)

        return None

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

    def _validate_vertex(self, x: int, y: int) -> bool:
        assert self._current_position is not None
        tile_type = self._state.get_tile(x, y)

        if tile_type == model.TileType.ANY:
            return True

        adjacent_v = self._enumerate_vertices(x, y)
        if len(adjacent_v) != 2:
            return False
        (a0_x, a0_y), (a1_x, a1_y) = adjacent_v
        a0_c = self._is_corner(a0_x, a0_y)
        a1_c = self._is_corner(a1_x, a1_y)
        if a0_c is None or a1_c is None:
            return False
        has_adjacent_corner = a0_c or a1_c

        if tile_type == model.TileType.STRAIGHT:
            return self._is_corner(x, y) is False and has_adjacent_corner
        elif tile_type == model.TileType.CORNER:
            return self._is_corner(x, y) is True and not has_adjacent_corner
        assert False

    def _enumerate_vertices(self, x: int, y: int) -> set[typing.Tuple[int, int]]:
        vertices: set[typing.Tuple[int, int]] = set()
        for d, v_x, v_y in self._enumerate_lines(x, y):
            vertices.add((v_x, v_y))
            if d == _LineDirection.HORIZONTAL:
                vertices.add((v_x + 1, v_y))
            elif d == _LineDirection.VERTICAL:
                vertices.add((v_x, v_y + 1))

        vertices.remove((x, y))
        return vertices

    def _is_corner(self, x: int, y: int) -> typing.Optional[bool]:
        lines = self._enumerate_lines(x, y)
        if len(lines) != 2:
            return None

        (d_a, _, _), (d_b, _, _) = lines
        return d_a != d_b
