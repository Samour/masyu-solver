import enum
import typing


class TileType(enum.Enum):
    ANY = 1
    CORNER = 2
    STRAIGHT = 3


class PuzzleState:

    def __init__(self, width: int, height: int):
        self._width: int = 0
        self._height: int = 0
        self._tiles: list[list[TileType]] = []
        self.reset(width, height)

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def reset(self, width: int, height: int) -> None:
        assert width > 0 and height > 0
        self._width = width
        self._height = height
        self._tiles = [[TileType.ANY for _y in range(height)] for _x in range(width)]

    def get_tile(self, x: int, y: int) -> typing.Optional[TileType]:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None

        return self._tiles[x][y]

    def set_tile(self, x: int, y: int, tile: TileType) -> None:
        assert x >= 0 and x < self.width and y >= 0 and y < self.height
        self._tiles[x][y] = tile
