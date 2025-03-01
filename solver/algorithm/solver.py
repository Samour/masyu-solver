from solver import model
from . import positions, vertex


class Solver:

    def __init__(self, puzzle_state: model.PuzzleState):
        self._state = puzzle_state
        self._positions: set[positions.SolverPosition] = set()
        self._vertex_solvers: list[vertex.VertexSolver] = [
            vertex.FillEmptyEdgesVS(puzzle_state=puzzle_state),
            vertex.OnlyLineOptionVS(puzzle_state=puzzle_state),
            vertex.DeadEndVS(puzzle_state=puzzle_state),
            vertex.StraightLineTileVS(puzzle_state=puzzle_state),
            vertex.CornerNextToStraightTileVS(puzzle_state=puzzle_state),
            vertex.CornerTileVS(puzzle_state=puzzle_state),
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
                    self._positions.add((x, y))

        for y in range(self._state.height):
            for x in range(self._state.width - 1):
                if self._state.get_hline(x, y) != model.LineState.ANY:
                    self._positions.add((x, y))
                    self._positions.add((x + 1, y))

        for y in range(self._state.height - 1):
            for x in range(self._state.width):
                if self._state.get_vline(x, y) != model.LineState.ANY:
                    self._positions.add((x, y))
                    self._positions.add((x, y + 1))

    def _serve(self) -> None:
        (x, y) = self._positions.pop()
        tile = self._state.get_tile(x, y)
        assert tile is not None
        v = positions.Vertex(puzzle_state=self._state, x=x, y=y)
        if v.is_filled and v.type == model.TileType.ANY:
            return

        for solver in self._vertex_solvers:
            updates = solver.make_updates(v)
            if len(updates) > 0:
                self._positions.update(updates)
                self._positions.add((x, y))
                break
