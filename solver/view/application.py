import tkinter as tk
from tkinter import filedialog
import typing
from solver import model, serialization
from . import puzzle, sizeselector


class Application(tk.Frame):

    def __init__(self, master: tk.Tk, puzzle_state: model.PuzzleState):
        super().__init__(master)
        self._puzzle_state = puzzle_state
        self._puzzle_view: typing.Optional[puzzle.PuzzleView] = None
        self._change_size_button: typing.Optional[_ChangeSizeButton] = None
        self._save_load_controls: typing.Optional[_SaveLoadControls] = None

    def render(self) -> None:
        if self._puzzle_view is not None:
            self._puzzle_view.destroy()
        if self._change_size_button is not None:
            self._change_size_button.destroy()
        if self._save_load_controls is not None:
            self._save_load_controls.destroy()

        self.pack(padx=50, pady=30)
        self._puzzle_view = puzzle.PuzzleView(self, puzzle_state=self._puzzle_state)
        self._puzzle_view.render()

        self._change_size_button = _ChangeSizeButton(
            self,
            puzzle_state=self._puzzle_state,
            rerender_puzzle=self._puzzle_view.render,
        )
        self._change_size_button.render()
        self._save_load_controls = _SaveLoadControls(
            self, puzzle_state=self._puzzle_state
        )
        self._save_load_controls.render()


class _ChangeSizeButton(tk.Frame):

    def __init__(
        self,
        master: tk.Frame,
        puzzle_state: model.PuzzleState,
        rerender_puzzle: typing.Callable[[], None],
    ):
        super().__init__(master)
        self._puzzle_state = puzzle_state
        self._rerender_puzzle = rerender_puzzle

    def render(self) -> None:
        self._size_button = tk.Button(
            self, text="Change size", command=self._on_changesize
        )
        self._size_button.pack()
        self.pack(pady=5)

    def _on_changesize(self) -> None:
        size_selector = sizeselector.SizeSelector(
            self, on_resize=self._on_changesize_confirm
        )
        size_selector.render()
        size_selector.grab_set()

    def _on_changesize_confirm(self, width: int, height: int) -> None:
        self._puzzle_state.reset(width, height)
        self._rerender_puzzle()


class _SaveLoadControls(tk.Frame):

    def __init__(self, master: tk.Frame, puzzle_state: model.PuzzleState):
        super().__init__(master)
        self._puzzle_state = puzzle_state
        self._load_button: typing.Optional[tk.Button] = None
        self._save_button: typing.Optional[tk.Button] = None

    def render(self) -> None:
        if self._load_button is not None:
            self._load_button.destroy()
        if self._save_button is not None:
            self._save_button.destroy()

        self._load_button = tk.Button(self, text="Load puzzle")
        self._load_button.pack(side="left", padx=5)
        self._save_button = tk.Button(
            self, text="Save puzzle", command=self._on_save_click
        )
        self._save_button.pack(padx=5)
        self.pack(pady=5)

    def _on_save_click(self) -> None:
        fh = filedialog.asksaveasfile()
        if fh is None:
            return

        with fh:
            serialization.PuzzleSerializer(fh).serialize(self._puzzle_state)


def main(puzzle_state: model.PuzzleState) -> None:
    root = tk.Tk()
    app = Application(root, puzzle_state)
    root.title("Masyu Solver")
    root.geometry("+500+200")
    app.render()
    root.mainloop()
