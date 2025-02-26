import tkinter as tk
import typing
import enum


class _Colours:
    CANVAS_BG = "white"
    DOT = "black"


class _Coords:
    OFFSET = 2
    TILE_SIZE = 30
    CLICK_PROXIMITY = 10

    class Dot:
        RADIUS = 1

    @staticmethod
    def map_to_tile(x: int, y: int) -> typing.Optional[typing.Tuple[int, int]]:
        tile_x = _Coords._map_tile_coord(x)
        tile_y = _Coords._map_tile_coord(y)
        return (tile_x, tile_y) if tile_x is not None and tile_y is not None else None

    @staticmethod
    def _map_tile_coord(v: int) -> typing.Optional[int]:
        tile_v = (v - _Coords.OFFSET) // _Coords.TILE_SIZE
        tile_center = (tile_v + 0.5) * _Coords.TILE_SIZE
        delta = abs(v - _Coords.OFFSET - tile_center)
        return tile_v if delta < _Coords.CLICK_PROXIMITY else None


class PuzzleView(tk.Frame):

    def __init__(self, master: tk.Frame):
        super().__init__(master)
        self._canvas: typing.Optional[tk.Canvas] = None
        self._tiles: list[list[_Tile]] = []

    def render(self) -> None:
        if self._canvas is not None:
            self._canvas.destroy()

        puzzle_width = 5
        puzzle_height = 5

        self._canvas = tk.Canvas(
            master=self,
            width=puzzle_width * _Coords.TILE_SIZE,
            height=puzzle_height * _Coords.TILE_SIZE,
            bg=_Colours.CANVAS_BG,
        )
        self._canvas.pack()
        self.pack()

        # There's a disagreement here between pylance and mymy
        # It's only possible to keep one of them happy, so decided to go with mypy
        # This does mean that it has squigly lines in VSCode
        self._canvas.bind("<Button-1>", self._handle_leftclick)
        self._canvas.bind("<Button-3>", self._handle_rightclick)

        self._tiles = [
            [_Tile(x, y) for y in range(puzzle_height)] for x in range(puzzle_width)
        ]
        for column in self._tiles:
            for tile in column:
                tile.draw(self._canvas)

    def _handle_leftclick(self, e: tk.Event) -> None:  # type: ignore[type-arg]
        coords = _Coords.map_to_tile(e.x, e.y)
        if coords is None:
            return

        tile = self._tiles[coords[0]][coords[1]]
        tile.next_type()

    def _handle_rightclick(self, e: tk.Event) -> None:  # type: ignore[type-arg]
        coords = _Coords.map_to_tile(e.x, e.y)
        if coords is None:
            return

        tile = self._tiles[coords[0]][coords[1]]
        tile.previous_type()


class _TileType(enum.Enum):
    ANY = 1
    CORNER = 2
    STRAIGHT = 3


class _Tile:

    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y
        self._type: _TileType = _TileType.ANY
        self._handle: typing.Optional[int] = None

    def draw(self, canvas: tk.Canvas) -> None:
        if self._handle is not None:
            canvas.delete(self._handle)

        self._draw_dot(canvas)

    def _draw_dot(self, canvas: tk.Canvas) -> None:
        tile_x = (self._x + 0.5) * _Coords.TILE_SIZE
        tile_y = (self._y + 0.5) * _Coords.TILE_SIZE

        dot_x0 = tile_x - _Coords.Dot.RADIUS + _Coords.OFFSET
        dot_x1 = tile_x + _Coords.Dot.RADIUS + _Coords.OFFSET
        dot_y0 = tile_y - _Coords.Dot.RADIUS + _Coords.OFFSET
        dot_y1 = tile_y + _Coords.Dot.RADIUS + _Coords.OFFSET

        self._handle = canvas.create_oval(
            dot_x0, dot_y0, dot_x1, dot_y1, fill=_Colours.DOT, outline=_Colours.DOT
        )

    def next_type(self) -> None:
        print(f"Move ({self._x}, {self._y}) to next type")

    def previous_type(self) -> None:
        print(f"Move ({self._x}, {self._y}) to previous type")
