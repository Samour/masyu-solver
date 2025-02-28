import tkinter as tk
import typing
from solver import model


class _Colours:
    CANVAS_BG = "white"
    DOT = "black"
    CIRCLE_OUTLINE = "black"
    CIRCLE_INNER = "white"


class _Coords:
    OFFSET = 2
    TILE_SIZE = 30
    CLICK_PROXIMITY = 10

    class Dot:
        RADIUS = 1

        @staticmethod
        def get_rect(x: int, y: int) -> typing.Tuple[float, float, float, float]:
            return _Coords._get_rect_for_circle(x, y, _Coords.Dot.RADIUS)

    class Circle:
        RADIUS = 5

        @staticmethod
        def get_rect(x: int, y: int) -> typing.Tuple[float, float, float, float]:
            return _Coords._get_rect_for_circle(x, y, _Coords.Circle.RADIUS)

    @staticmethod
    def _get_rect_for_circle(
        x: int, y: int, radius: int
    ) -> typing.Tuple[float, float, float, float]:
        tile_x = (x + 0.5) * _Coords.TILE_SIZE
        tile_y = (y + 0.5) * _Coords.TILE_SIZE

        circle_x0 = tile_x - radius + _Coords.OFFSET
        circle_x1 = tile_x + radius + _Coords.OFFSET
        circle_y0 = tile_y - radius + _Coords.OFFSET
        circle_y1 = tile_y + radius + _Coords.OFFSET

        return circle_x0, circle_y0, circle_x1, circle_y1

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

    def __init__(self, master: tk.Frame, puzzle_state: model.PuzzleState):
        super().__init__(master)
        self._canvas: typing.Optional[tk.Canvas] = None
        self._tiles: list[list[_Tile]] = []

        self._puzzle_state = puzzle_state

    def render(self) -> None:
        if self._canvas is not None:
            self._canvas.destroy()

        self._canvas = tk.Canvas(
            master=self,
            width=self._puzzle_state.width * _Coords.TILE_SIZE,
            height=self._puzzle_state.height * _Coords.TILE_SIZE,
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
            [_Tile(self._puzzle_state, x, y) for y in range(self._puzzle_state.height)]
            for x in range(self._puzzle_state.width)
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
        assert self._canvas is not None
        tile.draw(self._canvas)

    def _handle_rightclick(self, e: tk.Event) -> None:  # type: ignore[type-arg]
        coords = _Coords.map_to_tile(e.x, e.y)
        if coords is None:
            return

        tile = self._tiles[coords[0]][coords[1]]
        tile.previous_type()
        assert self._canvas is not None
        tile.draw(self._canvas)


class _Tile:

    def __init__(self, puzzle_state: model.PuzzleState, x: int, y: int):
        self._puzzle_state = puzzle_state
        self._x = x
        self._y = y
        self._handle: typing.Optional[int] = None

    @property
    def _type(self) -> model.TileType:
        tile_type = self._puzzle_state.get_tile(self._x, self._y)
        assert tile_type is not None
        return tile_type

    def _set_tile(self, tile: model.TileType) -> None:
        self._puzzle_state.set_tile(self._x, self._y, tile)

    def draw(self, canvas: tk.Canvas) -> None:
        if self._handle is not None:
            canvas.delete(self._handle)

        if self._type == model.TileType.ANY:
            self._draw_dot(canvas)
        elif self._type == model.TileType.CORNER:
            self._draw_solid_circle(canvas)
        elif self._type == model.TileType.STRAIGHT:
            self._draw_hollow_circle(canvas)

    def _draw_dot(self, canvas: tk.Canvas) -> None:
        dot_x0, dot_y0, dot_x1, dot_y1 = _Coords.Dot.get_rect(self._x, self._y)
        self._handle = canvas.create_oval(
            dot_x0, dot_y0, dot_x1, dot_y1, fill=_Colours.DOT, outline=_Colours.DOT
        )

    def _draw_solid_circle(self, canvas: tk.Canvas) -> None:
        circle_x0, circle_y0, circle_x1, circle_y1 = _Coords.Circle.get_rect(
            self._x, self._y
        )
        self._handle = canvas.create_oval(
            circle_x0,
            circle_y0,
            circle_x1,
            circle_y1,
            fill=_Colours.CIRCLE_OUTLINE,
            outline=_Colours.CIRCLE_OUTLINE,
        )

    def _draw_hollow_circle(self, canvas: tk.Canvas) -> None:
        circle_x0, circle_y0, circle_x1, circle_y1 = _Coords.Circle.get_rect(
            self._x, self._y
        )
        self._handle = canvas.create_oval(
            circle_x0,
            circle_y0,
            circle_x1,
            circle_y1,
            fill=_Colours.CIRCLE_INNER,
            outline=_Colours.CIRCLE_OUTLINE,
        )

    def next_type(self) -> None:
        if self._type == model.TileType.ANY:
            self._set_tile(model.TileType.CORNER)
        elif self._type == model.TileType.CORNER:
            self._set_tile(model.TileType.STRAIGHT)
        elif self._type == model.TileType.STRAIGHT:
            self._set_tile(model.TileType.ANY)

    def previous_type(self) -> None:
        if self._type == model.TileType.ANY:
            self._set_tile(model.TileType.STRAIGHT)
        elif self._type == model.TileType.STRAIGHT:
            self._set_tile(model.TileType.CORNER)
        elif self._type == model.TileType.CORNER:
            self._set_tile(model.TileType.ANY)
