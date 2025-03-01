import enum
import typing


class TileType(enum.Enum):
    ANY = 1
    CORNER = 2
    STRAIGHT = 3


class LineState(enum.Enum):
    ANY = 1
    LINE = 2
    EMPTY = 3


class PuzzleState:

    def __init__(self, width: int, height: int):
        self._width: int = 0
        self._height: int = 0
        self._tiles: list[list[TileType]] = []
        self._hlines: list[list[LineState]] = []
        self._vlines: list[list[LineState]] = []
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
        self._hlines = [
            [LineState.ANY for _y in range(height)] for _x in range(width - 1)
        ]
        self._vlines = [
            [LineState.ANY for _y in range(height - 1)] for _x in range(width)
        ]

    def apply(self, state: "PuzzleState") -> None:
        self.reset(state.width, state.height)
        for y in range(state.height):
            for x in range(state.width):
                tile = state.get_tile(x, y)
                assert tile is not None
                self.set_tile(x, y, tile)
        for y in range(state.height):
            for x in range(state.width - 1):
                hline = state.get_hline(x, y)
                assert hline is not None
                self.set_hline(x, y, hline)
        for y in range(state.height - 1):
            for x in range(state.width):
                vline = state.get_vline(x, y)
                assert vline is not None
                self.set_vline(x, y, vline)

    def get_tile(self, x: int, y: int) -> typing.Optional[TileType]:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None

        return self._tiles[x][y]

    def set_tile(self, x: int, y: int, tile: TileType) -> None:
        assert x >= 0 and x < self.width and y >= 0 and y < self.height
        self._tiles[x][y] = tile

    def get_hline(self, x: int, y: int) -> typing.Optional[LineState]:
        if x < 0 or x >= self.width - 1 or y < 0 or y >= self.height:
            return None

        return self._hlines[x][y]

    def set_hline(self, x: int, y: int, state: LineState) -> None:
        assert x >= 0 and x < self.width - 1 and y >= 0 and y < self.height
        self._hlines[x][y] = state

    def get_vline(self, x: int, y: int) -> typing.Optional[LineState]:
        if x < 0 or x >= self.width or y < 0 or y >= self.height - 1:
            return None

        return self._vlines[x][y]

    def set_vline(self, x: int, y: int, state: LineState) -> None:
        assert x >= 0 and x < self.width and y >= 0 and y < self.height - 1
        self._vlines[x][y] = state
