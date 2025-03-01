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


class VertexSolver(abc.ABC):

    def __init__(self, puzzle_state: model.PuzzleState):
        self.puzzle_state = puzzle_state
        self.affected: positions.AffectedPositions = positions.AffectedPositions(
            puzzle_state=puzzle_state
        )

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
            updates.update(self.affected.tiles_for_vline(vertex.x, vertex.y - 1))
        if vertex.line_down == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y, model.LineState.EMPTY)
            updates.update(self.affected.tiles_for_vline(vertex.x, vertex.y))
        if vertex.line_left == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x - 1, vertex.y, model.LineState.EMPTY)
            updates.update(self.affected.tiles_for_hline(vertex.x - 1, vertex.y))
        if vertex.line_right == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x, vertex.y, model.LineState.EMPTY)
            updates.update(self.affected.tiles_for_hline(vertex.x, vertex.y))

        return updates


class DeadEndVS(VertexSolver):

    def make_updates(self, vertex: Vertex) -> set[positions.SolverPosition]:
        if vertex.count_any != 1:
            return set()

        if vertex.line_up == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y - 1, model.LineState.EMPTY)
            return self.affected.tiles_for_vline(vertex.x, vertex.y - 1)
        elif vertex.line_down == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y, model.LineState.EMPTY)
            return self.affected.tiles_for_vline(vertex.x, vertex.y)
        elif vertex.line_left == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x - 1, vertex.y, model.LineState.EMPTY)
            return self.affected.tiles_for_hline(vertex.x - 1, vertex.y)
        elif vertex.line_right == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x, vertex.y, model.LineState.EMPTY)
            return self.affected.tiles_for_hline(vertex.x, vertex.y)

        return set()


class OnlyLineOptionVS(VertexSolver):

    def make_updates(self, vertex: Vertex) -> set[positions.SolverPosition]:
        if vertex.count_lines != 1 or vertex.count_any != 1:
            return set()

        if vertex.line_up == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y - 1, model.LineState.LINE)
            return self.affected.tiles_for_vline(vertex.x, vertex.y - 1)
        elif vertex.line_down == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y, model.LineState.LINE)
            return self.affected.tiles_for_vline(vertex.x, vertex.y)
        elif vertex.line_left == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x - 1, vertex.y, model.LineState.LINE)
            return self.affected.tiles_for_hline(vertex.x - 1, vertex.y)
        elif vertex.line_right == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x, vertex.y, model.LineState.LINE)
            return self.affected.tiles_for_hline(vertex.x, vertex.y)

        return set()


class StraightLineTileVS(VertexSolver):

    def make_updates(self, vertex: Vertex) -> set[positions.SolverPosition]:
        if vertex.type != model.TileType.STRAIGHT or vertex.count_lines == 2:
            return set()

        if (
            vertex.line_down == model.LineState.LINE
            or vertex.line_up == model.LineState.LINE
            or not vertex.may_place_line_left
            or not vertex.may_place_line_right
        ):
            return self._populate_vertical(vertex)
        elif (
            vertex.line_left == model.LineState.LINE
            or vertex.line_right == model.LineState.LINE
            or not vertex.may_place_line_up
            or not vertex.may_place_line_down
        ):
            return self._populate_horizontal(vertex)

        return set()

    def _populate_horizontal(self, vertex: Vertex) -> set[positions.SolverPosition]:
        updates: set[positions.SolverPosition] = set()
        if vertex.line_left == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x - 1, vertex.y, model.LineState.LINE)
            updates.update(self.affected.tiles_for_hline(vertex.x - 1, vertex.y))
        if vertex.line_right == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x, vertex.y, model.LineState.LINE)
            updates.update(self.affected.tiles_for_hline(vertex.x, vertex.y))

        return updates

    def _populate_vertical(self, vertex: Vertex) -> set[positions.SolverPosition]:
        updates: set[positions.SolverPosition] = set()
        if vertex.line_up == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y - 1, model.LineState.LINE)
            updates.update(self.affected.tiles_for_vline(vertex.x, vertex.y - 1))
        if vertex.line_down == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y, model.LineState.LINE)
            updates.update(self.affected.tiles_for_vline(vertex.x, vertex.y))

        return updates


class CornerNextToStraightTileVS(VertexSolver):

    def make_updates(self, vertex: Vertex) -> set[positions.SolverPosition]:
        for adjacent in vertex.adjacent_vertices:
            if adjacent.type != model.TileType.STRAIGHT or adjacent.count_lines != 2:
                continue

            compliment = self._get_compliment_corner(straight=adjacent, current=vertex)
            if compliment is None or compliment.may_be_corner:
                continue

            if adjacent.y < vertex.y and vertex.line_down == model.LineState.ANY:
                self.puzzle_state.set_vline(vertex.x, vertex.y, model.LineState.EMPTY)
                return self.affected.tiles_for_vline(vertex.x, vertex.y)
            elif adjacent.x > vertex.x and vertex.line_left == model.LineState.ANY:
                self.puzzle_state.set_hline(
                    vertex.x - 1, vertex.y, model.LineState.EMPTY
                )
                return self.affected.tiles_for_hline(vertex.x - 1, vertex.y)
            elif adjacent.y > vertex.y and vertex.line_up == model.LineState.ANY:
                self.puzzle_state.set_vline(
                    vertex.x, vertex.y - 1, model.LineState.EMPTY
                )
                return self.affected.tiles_for_vline(vertex.x, vertex.y - 1)
            elif adjacent.x < vertex.x and vertex.line_right == model.LineState.ANY:
                self.puzzle_state.set_hline(vertex.x, vertex.y, model.LineState.EMPTY)
                return self.affected.tiles_for_hline(vertex.x, vertex.y)

        return set()

    def _get_compliment_corner(
        self, straight: Vertex, current: Vertex
    ) -> typing.Optional[Vertex]:
        candidates: set[typing.Tuple[int, int]]
        if (
            straight.line_left == model.LineState.LINE
            and straight.line_right == model.LineState.LINE
        ):
            candidates = {(straight.x - 1, straight.y), (straight.x + 1, straight.y)}
        elif (
            straight.line_up == model.LineState.LINE
            and straight.line_down == model.LineState.LINE
        ):
            candidates = {(straight.x, straight.y - 1), (straight.x, straight.y + 1)}
        else:
            return None

        if (current.x, current.y) not in candidates:
            return None

        candidates.remove((current.x, current.y))
        x, y = candidates.pop()
        return Vertex(puzzle_state=self.puzzle_state, x=x, y=y)


class CornerTileVS(VertexSolver):

    def make_updates(self, vertex: Vertex) -> set[positions.SolverPosition]:
        if vertex.type != model.TileType.CORNER:
            return set()

        updates: set[positions.SolverPosition] = set()
        if vertex.line_up == model.LineState.LINE or not self._may_place_line_down(
            vertex
        ):
            updates.update(self._place_line_up(vertex))
            updates.update(self._block_line_down(vertex))
        if vertex.line_down == model.LineState.LINE or not self._may_place_line_up(
            vertex
        ):
            updates.update(self._place_line_down(vertex))
            updates.update(self._block_line_up(vertex))
        if vertex.line_left == model.LineState.LINE or not self._may_place_line_right(
            vertex
        ):
            updates.update(self._place_line_left(vertex))
            updates.update(self._block_line_right(vertex))
        if vertex.line_right == model.LineState.LINE or not self._may_place_line_left(
            vertex
        ):
            updates.update(self._place_line_right(vertex))
            updates.update(self._block_line_left(vertex))

        if not self._may_place_line_up(vertex):
            updates.update(self._block_line_up(vertex))
        if not self._may_place_line_down(vertex):
            updates.update(self._block_line_down(vertex))
        if not self._may_place_line_left(vertex):
            updates.update(self._block_line_left(vertex))
        if not self._may_place_line_right(vertex):
            updates.update(self._block_line_right(vertex))

        return updates

    def _may_place_line_down(self, vertex: Vertex) -> bool:
        if not vertex.may_place_line_down:
            return False

        down_vertex = vertex.adjacent_vertex_down
        return down_vertex is not None and down_vertex.may_place_line_down

    def _may_place_line_up(self, vertex: Vertex) -> bool:
        if not vertex.may_place_line_up:
            return False

        up_vertex = vertex.adjacent_vertex_up
        return up_vertex is not None and up_vertex.may_place_line_up

    def _may_place_line_left(self, vertex: Vertex) -> bool:
        if not vertex.may_place_line_left:
            return False

        left_vertex = vertex.adjacent_vertex_left
        return left_vertex is not None and left_vertex.may_place_line_left

    def _may_place_line_right(self, vertex: Vertex) -> bool:
        if not vertex.may_place_line_right:
            return False

        right_vertex = vertex.adjacent_vertex_right
        return right_vertex is not None and right_vertex.may_place_line_right

    def _place_line_up(self, vertex: Vertex) -> set[positions.SolverPosition]:
        updates: set[positions.SolverPosition] = set()
        if vertex.line_up == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y - 1, model.LineState.LINE)
            updates.update(self.affected.tiles_for_vline(vertex.x, vertex.y - 1))

        up_vertex = vertex.adjacent_vertex_up
        if up_vertex is not None and up_vertex.line_up == model.LineState.ANY:
            self.puzzle_state.set_vline(
                up_vertex.x, up_vertex.y - 1, model.LineState.LINE
            )
            updates.update(self.affected.tiles_for_vline(up_vertex.x, up_vertex.y - 1))

        return updates

    def _place_line_down(self, vertex: Vertex) -> set[positions.SolverPosition]:
        updates: set[positions.SolverPosition] = set()
        if vertex.line_down == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y, model.LineState.LINE)
            updates.update(self.affected.tiles_for_vline(vertex.x, vertex.y))

        down_vertex = vertex.adjacent_vertex_down
        if down_vertex is not None and down_vertex.line_down == model.LineState.ANY:
            self.puzzle_state.set_vline(
                down_vertex.x, down_vertex.y, model.LineState.LINE
            )
            updates.update(self.affected.tiles_for_vline(down_vertex.x, down_vertex.y))

        return updates

    def _place_line_left(self, vertex: Vertex) -> set[positions.SolverPosition]:
        updates: set[positions.SolverPosition] = set()
        if vertex.line_left == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x - 1, vertex.y, model.LineState.LINE)
            updates.update(self.affected.tiles_for_hline(vertex.x - 1, vertex.y))

        left_vertex = vertex.adjacent_vertex_left
        if left_vertex is not None and left_vertex.line_left == model.LineState.ANY:
            self.puzzle_state.set_hline(
                left_vertex.x - 1, left_vertex.y, model.LineState.LINE
            )
            updates.update(
                self.affected.tiles_for_hline(left_vertex.x - 1, left_vertex.y)
            )

        return updates

    def _place_line_right(self, vertex: Vertex) -> set[positions.SolverPosition]:
        updates: set[positions.SolverPosition] = set()
        if vertex.line_right == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x, vertex.y, model.LineState.LINE)
            updates.update(self.affected.tiles_for_hline(vertex.x, vertex.y))

        right_vertex = vertex.adjacent_vertex_right
        if right_vertex is not None and right_vertex.line_right == model.LineState.ANY:
            self.puzzle_state.set_hline(
                right_vertex.x, right_vertex.y, model.LineState.LINE
            )
            updates.update(
                self.affected.tiles_for_hline(right_vertex.x, right_vertex.y)
            )

        return updates

    def _block_line_up(self, vertex: Vertex) -> set[positions.SolverPosition]:
        if vertex.line_up != model.LineState.ANY:
            return set()

        self.puzzle_state.set_vline(vertex.x, vertex.y - 1, model.LineState.EMPTY)
        return self.affected.tiles_for_vline(vertex.x, vertex.y - 1)

    def _block_line_down(self, vertex: Vertex) -> set[positions.SolverPosition]:
        if vertex.line_down != model.LineState.ANY:
            return set()

        self.puzzle_state.set_vline(vertex.x, vertex.y, model.LineState.EMPTY)
        return self.affected.tiles_for_vline(vertex.x, vertex.y)

    def _block_line_left(self, vertex: Vertex) -> set[positions.SolverPosition]:
        if vertex.line_left != model.LineState.ANY:
            return set()

        self.puzzle_state.set_hline(vertex.x - 1, vertex.y, model.LineState.EMPTY)
        return self.affected.tiles_for_hline(vertex.x - 1, vertex.y)

    def _block_line_right(self, vertex: Vertex) -> set[positions.SolverPosition]:
        if vertex.line_right != model.LineState.ANY:
            return set()

        self.puzzle_state.set_hline(vertex.x, vertex.y, model.LineState.EMPTY)
        return self.affected.tiles_for_hline(vertex.x, vertex.y)
