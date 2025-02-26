import tkinter as tk
import typing


class _Colours:
    CANVAS_BG = "white"
    DOT = "black"


class _Coords:
    OFFSET = 2
    TILE_SIZE = 30

    class Dot:
        RADIUS = 1


class PuzzleView(tk.Frame):

    def __init__(self, master: tk.Frame):
        super().__init__(master)
        self._canvas: typing.Optional[tk.Canvas] = None

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

        for y in range(puzzle_height):
            for x in range(puzzle_height):
                self._draw_dot(x, y)

    def _draw_dot(self, x: int, y: int) -> None:
        assert self._canvas is not None

        tile_x = (x + 0.5) * _Coords.TILE_SIZE
        tile_y = (y + 0.5) * _Coords.TILE_SIZE

        dot_x0 = tile_x - _Coords.Dot.RADIUS + _Coords.OFFSET
        dot_x1 = tile_x + _Coords.Dot.RADIUS + _Coords.OFFSET
        dot_y0 = tile_y - _Coords.Dot.RADIUS + _Coords.OFFSET
        dot_y1 = tile_y + _Coords.Dot.RADIUS + _Coords.OFFSET
        self._canvas.create_oval(
            dot_x0, dot_y0, dot_x1, dot_y1, fill=_Colours.DOT, outline=_Colours.DOT
        )
