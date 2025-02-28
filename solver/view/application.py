import tkinter as tk
import typing
from solver import model
from . import puzzle, sizeselector


class Application(tk.Frame):

    def __init__(self, master: tk.Tk, puzzle_state: model.PuzzleState):
        super().__init__(master)
        self._puzzle_state = puzzle_state
        self._puzzle_view: typing.Optional[puzzle.PuzzleView] = None
        self._size_button: typing.Optional[tk.Button] = None

    def render(self) -> None:
        if self._puzzle_view is not None:
            self._puzzle_view.destroy()
        if self._size_button is not None:
            self._size_button.destroy()

        self.pack(padx=50, pady=30)
        self._puzzle_view = puzzle.PuzzleView(self, self._puzzle_state)
        self._puzzle_view.render()

        self._size_button = tk.Button(
            self, text="Change size", command=self._on_changesize
        )
        self._size_button.pack()

    def _on_changesize(self) -> None:
        size_selector = sizeselector.SizeSelector(self, on_resize=self._on_changesize_confirm)
        size_selector.render()
        size_selector.grab_set()
    
    def _on_changesize_confirm(self, width: int, height: int) -> None:
        self._puzzle_state.reset(width, height)
        assert self._puzzle_view is not None
        self._puzzle_view.render()


def main(puzzle_state: model.PuzzleState) -> None:
    root = tk.Tk()
    app = Application(root, puzzle_state)
    root.title("Masyu Solver")
    root.geometry("+500+200")
    app.render()
    root.mainloop()
