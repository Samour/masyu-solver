import enum
import typing


class ItemType(enum.Enum):
    TILE = 1
    HLINE = 2
    VLINE = 3


SolverPosition = typing.Tuple[ItemType, int, int]


def tiles_for_hline(x: int, y: int) -> set[SolverPosition]:
    return {(ItemType.TILE, x, y), (ItemType.TILE, x + 1, y)}


def tiles_for_vline(x: int, y: int) -> set[SolverPosition]:
    return {(ItemType.TILE, x, y), (ItemType.TILE, x, y + 1)}
