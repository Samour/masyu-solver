import typing
from solver import model


SolverPosition = typing.Tuple[int, int]


class AffectedPositions:

    def __init__(self, puzzle_state: model.PuzzleState):
        self._puzzle_state = puzzle_state

    def tiles_for_hline(self, x: int, y: int) -> set[SolverPosition]:
        tiles: set[SolverPosition] = {(x, y), (x + 1, y)}
        if self._puzzle_state.get_tile(x - 1, y) is not None:
            tiles.add((x - 1, y))
        if self._puzzle_state.get_tile(x + 2, y) is not None:
            tiles.add((x + 2, y))

        return tiles

    def tiles_for_vline(self, x: int, y: int) -> set[SolverPosition]:
        tiles: set[SolverPosition] = {(x, y), (x, y + 1)}
        if self._puzzle_state.get_tile(x, y - 1) is not None:
            tiles.add((x, y - 1))
        if self._puzzle_state.get_tile(x, y + 2) is not None:
            tiles.add((x, y + 2))

        return tiles
