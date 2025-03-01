from solver import model
from . import positions, vertex


class Solver:

    def __init__(self, puzzle_state: model.PuzzleState):
        self._state = puzzle_state
        self._positions: set[positions.SolverPosition] = set()
        self._vertex_solvers: list[vertex.VertexSolver] = [
            vertex.FillEmptyEdgesVS(puzzle_state=puzzle_state),
            vertex.OnlyLineOptionVS(puzzle_state=puzzle_state),
        ]

    def solve(self) -> None:
        self._load()

        while len(self._positions):
            self._serve()

    def _load(self) -> None:
        self._positions = set()
        for y in range(self._state.height):
            for x in range(self._state.width):
                if self._state.get_tile(x, y) != model.TileType.ANY:
                    self._positions.add((positions.ItemType.TILE, x, y))

        for y in range(self._state.height):
            for x in range(self._state.width - 1):
                if self._state.get_hline(x, y) != model.LineState.ANY:
                    self._positions.add((positions.ItemType.HLINE, x, y))
                    self._positions.add((positions.ItemType.TILE, x, y))
                    self._positions.add((positions.ItemType.TILE, x + 1, y))

        for y in range(self._state.height - 1):
            for x in range(self._state.width):
                if self._state.get_vline(x, y) != model.LineState.ANY:
                    self._positions.add((positions.ItemType.VLINE, x, y))
                    self._positions.add((positions.ItemType.TILE, x, y))
                    self._positions.add((positions.ItemType.TILE, x, y + 1))

    def _serve(self) -> None:
        (itype, x, y) = self._positions.pop()
        if itype == positions.ItemType.TILE:
            self._serve_vertex(x, y)
        elif itype == positions.ItemType.HLINE:
            self._serve_hline(x, y)
        elif itype == positions.ItemType.VLINE:
            self._serve_vline(x, y)

    def _serve_vertex(self, x: int, y: int) -> None:
        tile = self._state.get_tile(x, y)
        assert tile is not None
        v = vertex.Vertex(puzzle_state=self._state, x=x, y=y)
        if v.is_filled:
            return

        for solver in self._vertex_solvers:
            updates = solver.make_updates(v)
            if len(updates) > 0:
                self._positions.update(updates)
                break

    def _serve_corner_tile(self, x: int, y: int) -> None:
        pass

    def _serve_straight_tile(self, x: int, y: int) -> None:
        pass

    def _serve_hline(self, x: int, y: int) -> None:
        pass

    def _serve_vline(self, x: int, y: int) -> None:
        pass
