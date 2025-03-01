import typing


SolverPosition = typing.Tuple[int, int]


def tiles_for_hline(x: int, y: int) -> set[SolverPosition]:
    return {(x, y), (x + 1, y)}


def tiles_for_vline(x: int, y: int) -> set[SolverPosition]:
    return {(x, y), (x, y + 1)}
