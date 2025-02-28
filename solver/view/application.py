import tkinter as tk
import typing
from solver import model
from . import puzzle, controls


class Application(tk.Frame):

    def __init__(self, master: tk.Tk, puzzle_state: model.PuzzleState):
        super().__init__(master)
        self._puzzle_state = puzzle_state
        self._puzzle_view: typing.Optional[puzzle.PuzzleView] = None
        self._puzzle_controls: typing.Optional[controls.PuzzleControls] = None
        self._save_load_controls: typing.Optional[controls.SaveLoadControls] = None

    def render(self) -> None:
        if self._puzzle_view is not None:
            self._puzzle_view.destroy()
        if self._puzzle_controls is not None:
            self._puzzle_controls.destroy()
        if self._save_load_controls is not None:
            self._save_load_controls.destroy()

        self.pack(padx=50, pady=30)
        self._puzzle_view = puzzle.PuzzleView(self, puzzle_state=self._puzzle_state)
        self._puzzle_view.render()

        self._puzzle_controls = controls.PuzzleControls(
            self,
            puzzle_state=self._puzzle_state,
            rerender_puzzle=self._puzzle_view.render,
        )
        self._puzzle_controls.render()
        self._save_load_controls = controls.SaveLoadControls(
            self,
            puzzle_state=self._puzzle_state,
            on_puzzle_load=self._puzzle_view.render,
        )
        self._save_load_controls.render()


def main(puzzle_state: model.PuzzleState) -> None:
    root = tk.Tk()
    app = Application(root, puzzle_state)
    root.title("Masyu Solver")
    root.geometry("+500+200")
    app.render()
    root.mainloop()
