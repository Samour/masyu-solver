import tkinter as tk
from solver import model
from . import rendering


class Cross:

    def __init__(
        self,
        puzzle_state: model.PuzzleState,
        x: int,
        y: int,
        orientation: rendering.LineType,
    ):
        self._puzzle_state = puzzle_state
        self._x = x
        self._y = y
        self._o = orientation
        self._handles: list[int] = []

    @property
    def _is_cross(self) -> bool:
        if self._o == rendering.LineType.HORIZONTAL:
            value = self._puzzle_state.get_hline(self._x, self._y)
        elif self._o == rendering.LineType.VERTICAL:
            value = self._puzzle_state.get_vline(self._x, self._y)
        else:
            assert False
        assert value is not None
        return value == model.LineState.EMPTY

    def draw(self, canvas: tk.Canvas) -> None:
        for h in self._handles:
            canvas.delete(h)
        self._handles = []

        if not self._is_cross:
            return

        c_x: float = self._x
        c_y: float = self._y
        if self._o == rendering.LineType.HORIZONTAL:
            c_x += 1
            c_y += 0.5
        elif self._o == rendering.LineType.VERTICAL:
            c_x += 0.5
            c_y += 1
        c_x *= rendering.Coords.TILE_SIZE
        c_y *= rendering.Coords.TILE_SIZE
        c_x += rendering.Coords.OFFSET
        c_y += rendering.Coords.OFFSET

        x0 = c_x - rendering.Coords.CROSS_RADIUS
        y0 = c_y - rendering.Coords.CROSS_RADIUS
        x1 = c_x + rendering.Coords.CROSS_RADIUS
        y1 = c_y + rendering.Coords.CROSS_RADIUS
        self._handles.append(
            canvas.create_line(x0, y0, x1, y1, fill=rendering.Colours.CROSS)
        )

        x0 = c_x + rendering.Coords.CROSS_RADIUS
        y0 = c_y - rendering.Coords.CROSS_RADIUS
        x1 = c_x - rendering.Coords.CROSS_RADIUS
        y1 = c_y + rendering.Coords.CROSS_RADIUS
        self._handles.append(
            canvas.create_line(x0, y0, x1, y1, fill=rendering.Colours.CROSS)
        )
