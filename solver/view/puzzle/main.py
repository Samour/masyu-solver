import tkinter as tk
import typing
from solver import model
from solver.view import state
from . import cross, rendering, tile


class PuzzleView(tk.Frame):

    def __init__(self, master: tk.Frame, view_state: state.ViewState):
        super().__init__(master)
        self._canvas: typing.Optional[tk.Canvas] = None
        self._tiles: list[list[tile.Tile]] = []
        self._hcrosses: list[list[cross.Cross]] = []
        self._vcrosses: list[list[cross.Cross]] = []

        self._state = view_state

    def render(self) -> None:
        if self._canvas is not None:
            self._canvas.destroy()

        self._canvas = tk.Canvas(
            master=self,
            width=self._state.puzzle_state.width * rendering.Coords.TILE_SIZE,
            height=self._state.puzzle_state.height * rendering.Coords.TILE_SIZE,
            bg=rendering.Colours.CANVAS_BG,
        )
        self._canvas.pack()
        self.pack()

        # There's a disagreement here between pylance and mymy
        # It's only possible to keep one of them happy, so decided to go with mypy
        # This does mean that it has squigly lines in VSCode
        self._canvas.bind("<Button-1>", self._handle_leftclick)
        self._canvas.bind("<Button-3>", self._handle_rightclick)

        self._tiles = [
            [
                tile.Tile(puzzle_state=self._state.puzzle_state, x=x, y=y)
                for y in range(self._state.puzzle_state.height)
            ]
            for x in range(self._state.puzzle_state.width)
        ]
        self._hcrosses = [
            [
                cross.Cross(
                    puzzle_state=self._state.puzzle_state,
                    x=x,
                    y=y,
                    orientation=rendering.LineType.HORIZONTAL,
                )
                for y in range(self._state.puzzle_state.height)
            ]
            for x in range(self._state.puzzle_state.width - 1)
        ]
        self._vcrosses = [
            [
                cross.Cross(
                    puzzle_state=self._state.puzzle_state,
                    x=x,
                    y=y,
                    orientation=rendering.LineType.VERTICAL,
                )
                for y in range(self._state.puzzle_state.height - 1)
            ]
            for x in range(self._state.puzzle_state.width)
        ]

        for tiles in self._tiles:
            for t in tiles:
                t.draw(self._canvas)
        for crosses in self._hcrosses:
            for c in crosses:
                c.draw(self._canvas)
        for crosses in self._vcrosses:
            for c in crosses:
                c.draw(self._canvas)
        
        self._state.register_rerender_hline(self._handle_rerender_hline)
        self._state.register_rerender_vline(self._handle_rerender_vline)

    def _handle_leftclick(self, e: tk.Event) -> None:  # type: ignore[type-arg]
        if self._state.view_mode == state.ViewMode.EDITING:
            self._handle_edit_leftclick(e.x, e.y)
        elif self._state.view_mode == state.ViewMode.SOLVING:
            self._handle_solve_leftclick(e.x, e.y)

    def _handle_edit_leftclick(self, x: int, y: int) -> None:
        coords = rendering.Coords.map_to_tile(x, y)
        if coords is None:
            return

        tile = self._tiles[coords[0]][coords[1]]
        tile.next_type()
        assert self._canvas is not None
        tile.draw(self._canvas)

    def _handle_solve_leftclick(self, c_x: int, c_y: int) -> None:
        line = self._map_to_line(c_x, c_y)
        if line is None:
            return
        d, x, y = line

        if d == rendering.LineType.HORIZONTAL:
            self._update_hline(x, y, True)
        elif d == rendering.LineType.VERTICAL:
            self._update_vline(x, y, True)

    def _handle_rightclick(self, e: tk.Event) -> None:  # type: ignore[type-arg]
        if self._state.view_mode == state.ViewMode.EDITING:
            self._handle_edit_rightclick(e.x, e.y)
        elif self._state.view_mode == state.ViewMode.SOLVING:
            self._handle_solve_rightclick(e.x, e.y)

    def _handle_edit_rightclick(self, x: int, y: int) -> None:
        coords = rendering.Coords.map_to_tile(x, y)
        if coords is None:
            return

        tile = self._tiles[coords[0]][coords[1]]
        tile.previous_type()
        assert self._canvas is not None
        tile.draw(self._canvas)

    def _handle_solve_rightclick(self, c_x: int, c_y: int) -> None:
        line = self._map_to_line(c_x, c_y)
        if line is None:
            return
        d, x, y = line

        if d == rendering.LineType.HORIZONTAL:
            self._update_hline(x, y, False)
        elif d == rendering.LineType.VERTICAL:
            self._update_vline(x, y, False)

    def _map_to_line(
        self, c_x: int, c_y: int
    ) -> typing.Optional[typing.Tuple[rendering.LineType, int, int]]:
        line = rendering.Coords.map_to_line(c_x, c_y)
        if line is None:
            return None
        d, x, y = line
        if x < 0 or y < 0:
            return None
        if d == rendering.LineType.HORIZONTAL:
            if (
                x >= self._state.puzzle_state.width - 1
                or y >= self._state.puzzle_state.height
            ):
                return None
        elif d == rendering.LineType.VERTICAL:
            if (
                x >= self._state.puzzle_state.width
                or y >= self._state.puzzle_state.height - 1
            ):
                return None

        return line

    def _update_hline(self, x: int, y: int, forward: bool) -> None:
        old_state = self._state.puzzle_state.get_hline(x, y)
        if old_state is None:
            return

        new_state = (
            self._next_line_state(old_state)
            if forward
            else self._previous_line_state(old_state)
        )
        self._state.puzzle_state.set_hline(x, y, new_state)
        assert self._canvas is not None
        self._tiles[x][y].draw(self._canvas)
        self._tiles[x + 1][y].draw(self._canvas)
        self._hcrosses[x][y].draw(self._canvas)

    def _update_vline(self, x: int, y: int, forward: bool) -> None:
        old_state = self._state.puzzle_state.get_vline(x, y)
        if old_state is None:
            return

        new_state = (
            self._next_line_state(old_state)
            if forward
            else self._previous_line_state(old_state)
        )
        self._state.puzzle_state.set_vline(x, y, new_state)
        assert self._canvas is not None
        self._tiles[x][y].draw(self._canvas)
        self._tiles[x][y + 1].draw(self._canvas)
        self._vcrosses[x][y].draw(self._canvas)

    def _next_line_state(self, line: model.LineState) -> model.LineState:
        if line == model.LineState.ANY:
            return model.LineState.LINE
        elif line == model.LineState.LINE:
            return model.LineState.EMPTY
        elif line == model.LineState.EMPTY:
            return model.LineState.ANY

    def _previous_line_state(self, line: model.LineState) -> model.LineState:
        if line == model.LineState.ANY:
            return model.LineState.EMPTY
        elif line == model.LineState.EMPTY:
            return model.LineState.LINE
        elif line == model.LineState.LINE:
            return model.LineState.ANY
    
    def _handle_rerender_hline(self, x: int, y: int) -> None:
        assert self._canvas is not None
        self._tiles[x][y].draw(self._canvas)
        self._tiles[x + 1][y].draw(self._canvas)
        self._hcrosses[x][y].draw(self._canvas)
    
    def _handle_rerender_vline(self, x: int, y: int) -> None:
        assert self._canvas is not None
        self._tiles[x][y].draw(self._canvas)
        self._tiles[x][y + 1].draw(self._canvas)
        self._vcrosses[x][y].draw(self._canvas)
