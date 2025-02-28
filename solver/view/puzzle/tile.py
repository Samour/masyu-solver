import tkinter as tk
from solver import model
from . import rendering


class Tile:

    def __init__(self, puzzle_state: model.PuzzleState, x: int, y: int):
        self._puzzle_state = puzzle_state
        self._x = x
        self._y = y
        self._handles: list[int] = []

    @property
    def _type(self) -> model.TileType:
        tile_type = self._puzzle_state.get_tile(self._x, self._y)
        assert tile_type is not None
        return tile_type

    @property
    def _line_up(self) -> bool:
        return (
            self._puzzle_state.get_vline(self._x, self._y - 1) == model.LineState.LINE
        )

    @property
    def _line_down(self) -> bool:
        return self._puzzle_state.get_vline(self._x, self._y) == model.LineState.LINE

    @property
    def _line_left(self) -> bool:
        return (
            self._puzzle_state.get_hline(self._x - 1, self._y) == model.LineState.LINE
        )

    @property
    def _line_right(self) -> bool:
        return self._puzzle_state.get_hline(self._x, self._y) == model.LineState.LINE

    def _set_tile(self, tile: model.TileType) -> None:
        self._puzzle_state.set_tile(self._x, self._y, tile)

    def draw(self, canvas: tk.Canvas) -> None:
        for h in self._handles:
            canvas.delete(h)
        self._handles = []

        if self._line_up:
            self._draw_line_up(canvas)
        if self._line_down:
            self._draw_line_down(canvas)
        if self._line_left:
            self._draw_line_left(canvas)
        if self._line_right:
            self._draw_line_right(canvas)

        if self._type == model.TileType.ANY:
            self._draw_dot(canvas)
        elif self._type == model.TileType.CORNER:
            self._draw_solid_circle(canvas)
        elif self._type == model.TileType.STRAIGHT:
            self._draw_hollow_circle(canvas)

    def _draw_line_up(self, canvas: tk.Canvas) -> None:
        x0 = (
            (self._x + 0.5) * rendering.Coords.TILE_SIZE
            - rendering.Coords.LINE_WIDTH
            + rendering.Coords.OFFSET
        )
        y0 = self._y * rendering.Coords.TILE_SIZE + rendering.Coords.OFFSET
        x1 = (
            (self._x + 0.5) * rendering.Coords.TILE_SIZE
            + rendering.Coords.LINE_WIDTH
            + rendering.Coords.OFFSET
        )
        y1 = (self._y + 0.5) * rendering.Coords.TILE_SIZE + rendering.Coords.OFFSET
        self._handles.append(
            canvas.create_rectangle(
                x0,
                y0,
                x1,
                y1,
                fill=rendering.Colours.LINE,
                outline=rendering.Colours.LINE,
            )
        )

    def _draw_line_down(self, canvas: tk.Canvas) -> None:
        x0 = (
            (self._x + 0.5) * rendering.Coords.TILE_SIZE
            - rendering.Coords.LINE_WIDTH
            + rendering.Coords.OFFSET
        )
        y0 = (self._y + 0.5) * rendering.Coords.TILE_SIZE + rendering.Coords.OFFSET
        x1 = (
            (self._x + 0.5) * rendering.Coords.TILE_SIZE
            + rendering.Coords.LINE_WIDTH
            + rendering.Coords.OFFSET
        )
        y1 = (self._y + 1) * rendering.Coords.TILE_SIZE + rendering.Coords.OFFSET
        self._handles.append(
            canvas.create_rectangle(
                x0,
                y0,
                x1,
                y1,
                fill=rendering.Colours.LINE,
                outline=rendering.Colours.LINE,
            )
        )

    def _draw_line_left(self, canvas: tk.Canvas) -> None:
        x0 = self._x * rendering.Coords.TILE_SIZE + rendering.Coords.OFFSET
        y0 = (
            (self._y + 0.5) * rendering.Coords.TILE_SIZE
            - rendering.Coords.LINE_WIDTH
            + rendering.Coords.OFFSET
        )
        x1 = (self._x + 0.5) * rendering.Coords.TILE_SIZE + rendering.Coords.OFFSET
        y1 = (
            (self._y + 0.5) * rendering.Coords.TILE_SIZE
            + rendering.Coords.LINE_WIDTH
            + rendering.Coords.OFFSET
        )
        self._handles.append(
            canvas.create_rectangle(
                x0,
                y0,
                x1,
                y1,
                fill=rendering.Colours.LINE,
                outline=rendering.Colours.LINE,
            )
        )

    def _draw_line_right(self, canvas: tk.Canvas) -> None:
        x0 = (self._x + 0.5) * rendering.Coords.TILE_SIZE + rendering.Coords.OFFSET
        y0 = (
            (self._y + 0.5) * rendering.Coords.TILE_SIZE
            - rendering.Coords.LINE_WIDTH
            + rendering.Coords.OFFSET
        )
        x1 = (self._x + 1) * rendering.Coords.TILE_SIZE + rendering.Coords.OFFSET
        y1 = (
            (self._y + 0.5) * rendering.Coords.TILE_SIZE
            + rendering.Coords.LINE_WIDTH
            + rendering.Coords.OFFSET
        )
        self._handles.append(
            canvas.create_rectangle(
                x0,
                y0,
                x1,
                y1,
                fill=rendering.Colours.LINE,
                outline=rendering.Colours.LINE,
            )
        )

    def _draw_dot(self, canvas: tk.Canvas) -> None:
        dot_x0, dot_y0, dot_x1, dot_y1 = rendering.Coords.Dot.get_rect(self._x, self._y)
        self._handles.append(
            canvas.create_oval(
                dot_x0,
                dot_y0,
                dot_x1,
                dot_y1,
                fill=rendering.Colours.DOT,
                outline=rendering.Colours.DOT,
            )
        )

    def _draw_solid_circle(self, canvas: tk.Canvas) -> None:
        circle_x0, circle_y0, circle_x1, circle_y1 = rendering.Coords.Circle.get_rect(
            self._x, self._y
        )
        self._handles.append(
            canvas.create_oval(
                circle_x0,
                circle_y0,
                circle_x1,
                circle_y1,
                fill=rendering.Colours.CIRCLE_OUTLINE,
                outline=rendering.Colours.CIRCLE_OUTLINE,
            )
        )

    def _draw_hollow_circle(self, canvas: tk.Canvas) -> None:
        circle_x0, circle_y0, circle_x1, circle_y1 = rendering.Coords.Circle.get_rect(
            self._x, self._y
        )
        self._handles.append(
            canvas.create_oval(
                circle_x0,
                circle_y0,
                circle_x1,
                circle_y1,
                fill=rendering.Colours.CIRCLE_INNER,
                outline=rendering.Colours.CIRCLE_OUTLINE,
            )
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
