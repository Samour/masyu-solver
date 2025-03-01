import abc
import enum
import typing
from solver import model


class _ItemType(enum.Enum):
    TILE = 1
    HLINE = 2
    VLINE = 3


_SolverPosition = typing.Tuple[_ItemType, int, int]


class Solver:
    
    def __init__(self, puzzle_state: model.PuzzleState):
        self._state = puzzle_state
        self._positions: set[_SolverPosition] = set()
        self._vertex_solvers: list[_VertexSolver] = [
            _FillEmptyEdgesPS(puzzle_state=puzzle_state)
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
                    self._positions.add((_ItemType.TILE, x, y))
        
        for y in range(self._state.height):
            for x in range(self._state.width - 1):
                if self._state.get_hline(x, y) != model.LineState.ANY:
                    self._positions.add((_ItemType.HLINE, x, y))
                    self._positions.add((_ItemType.TILE, x, y))
                    self._positions.add((_ItemType.TILE, x + 1, y))
        
        for y in range(self._state.height - 1):
            for x in range(self._state.width):
                if self._state.get_vline(x, y) != model.LineState.ANY:
                    self._positions.add((_ItemType.VLINE, x, y))
                    self._positions.add((_ItemType.TILE, x, y))
                    self._positions.add((_ItemType.TILE, x, y + 1))
    
    def _serve(self) -> None:
        (itype, x, y) = self._positions.pop()
        if itype == _ItemType.TILE:
            self._serve_vertex(x, y)
        elif itype == _ItemType.HLINE:
            self._serve_hline(x, y)
        elif itype == _ItemType.VLINE:
            self._serve_vline(x, y)

    def _serve_vertex(self, x: int, y: int) -> None:
        tile = self._state.get_tile(x, y)
        assert tile is not None
        vertex = _Vertex(puzzle_state=self._state, x=x, y=y)
        if vertex.is_filled:
            return
        
        for solver in self._vertex_solvers:
            updates = solver.make_updates(vertex)
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


class _Vertex:

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
    def is_filled(self) -> bool:
        return self._count_adjacent(model.LineState.ANY) == 0
    
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


class _VertexSolver(abc.ABC):

    def __init__(self, puzzle_state: model.PuzzleState):
        self.puzzle_state = puzzle_state
    
    @abc.abstractmethod
    def make_updates(self, vertex: _Vertex) -> set[_SolverPosition]:
        pass


class _FillEmptyEdgesPS(_VertexSolver):

    def make_updates(self, vertex: _Vertex) -> set[_SolverPosition]:
        if vertex.count_lines != 2:
            return set()
        
        updates: set[_SolverPosition] = set()
        if vertex.line_up == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y - 1, model.LineState.EMPTY)
            updates.add((_ItemType.VLINE, vertex.x, vertex.y - 1))
        if vertex.line_down == model.LineState.ANY:
            self.puzzle_state.set_vline(vertex.x, vertex.y, model.LineState.EMPTY)
            updates.add((_ItemType.VLINE, vertex.x, vertex.y))
        if vertex.line_left == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x - 1, vertex.y, model.LineState.EMPTY)
            updates.add((_ItemType.HLINE, vertex.x - 1, vertex.y))
        if vertex.line_right == model.LineState.ANY:
            self.puzzle_state.set_hline(vertex.x, vertex.y, model.LineState.EMPTY)
            updates.add((_ItemType.HLINE, vertex.x, vertex.y))
        
        return updates
