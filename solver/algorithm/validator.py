import enum
import typing
from solver import model
from . import positions


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


_LineSpec = typing.Tuple[_LineDirection, int, int]


class SolutionValidator:

    def __init__(self, puzzle_state: model.PuzzleState):
        self._state = puzzle_state
        self._vertices: set[typing.Tuple[int, int]] = set()
        self._lines: set[_LineSpec] = set()
        self._starting_point: typing.Optional[_LineSpec] = None
        self._current_position: typing.Optional[_LineSpec] = None
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
        if not self.validate_vertex(v_x, v_y):
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
    ) -> typing.Optional[typing.Tuple[typing.Tuple[int, int], _LineSpec]]:
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

    def _enumerate_lines(self, x: int, y: int) -> set[_LineSpec]:
        lines: set[_LineSpec] = set()
        if self._state.get_hline(x, y) == model.LineState.LINE:
            lines.add((_LineDirection.HORIZONTAL, x, y))
        if self._state.get_hline(x - 1, y) == model.LineState.LINE:
            lines.add((_LineDirection.HORIZONTAL, x - 1, y))
        if self._state.get_vline(x, y) == model.LineState.LINE:
            lines.add((_LineDirection.VERTICAL, x, y))
        if self._state.get_vline(x, y - 1) == model.LineState.LINE:
            lines.add((_LineDirection.VERTICAL, x, y - 1))

        return lines

    def validate_vertex(self, x: int, y: int) -> bool:
        vertex = positions.Vertex(puzzle_state=self._state, x=x, y=y)
        if vertex.is_filled and vertex.count_lines not in (0, 2):
            return False
        if vertex.count_lines > 2:
            return False

        if vertex.type == model.TileType.ANY:
            return True
        elif vertex.type == model.TileType.CORNER:
            return self._validate_corner_vertex(vertex)
        elif vertex.type == model.TileType.STRAIGHT:
            return self._validate_straight_vertex(vertex)

        assert False

    def _validate_corner_vertex(self, vertex: positions.Vertex) -> bool:
        if not vertex.may_be_corner:
            return False
        if vertex.line_up == model.LineState.LINE:
            up_vertex = vertex.adjacent_vertex_up
            if (
                up_vertex is None
                or not up_vertex.may_be_straight
                or not up_vertex.may_place_line_up
            ):
                return False
        if vertex.line_right == model.LineState.LINE:
            right_vertex = vertex.adjacent_vertex_right
            if (
                right_vertex is None
                or not right_vertex.may_be_straight
                or not right_vertex.may_place_line_right
            ):
                return False
        if vertex.line_down == model.LineState.LINE:
            down_vertex = vertex.adjacent_vertex_down
            if (
                down_vertex is None
                or not down_vertex.may_be_straight
                or not down_vertex.may_place_line_down
            ):
                return False
        if vertex.line_left == model.LineState.LINE:
            left_vertex = vertex.adjacent_vertex_left
            if (
                left_vertex is None
                or not left_vertex.may_be_straight
                or not left_vertex.may_place_line_left
            ):
                return False

        return True

    def _validate_straight_vertex(self, vertex: positions.Vertex) -> bool:
        if not vertex.may_be_straight:
            return False
        if (
            vertex.line_up == model.LineState.LINE
            or vertex.line_down == model.LineState.LINE
        ):
            up_vertex = vertex.adjacent_vertex_up
            down_vertex = vertex.adjacent_vertex_down
            if up_vertex is None or down_vertex is None:
                return False
            if not up_vertex.may_be_corner and not down_vertex.may_be_corner:
                return False
            if up_vertex.is_straight and not down_vertex.may_be_corner:
                return False
            if down_vertex.is_straight and not up_vertex.may_be_corner:
                return False
        if (
            vertex.line_left == model.LineState.LINE
            or vertex.line_right == model.LineState.LINE
        ):
            left_vertex = vertex.adjacent_vertex_left
            right_vertex = vertex.adjacent_vertex_right
            if left_vertex is None or right_vertex is None:
                return False
            if not left_vertex.may_be_corner and not right_vertex.may_be_corner:
                return False
            if left_vertex.is_straight and not right_vertex.may_be_corner:
                return False
            if right_vertex.is_straight and not left_vertex.may_be_corner:
                return False

        return True
