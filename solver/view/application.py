import tkinter as tk
import typing
from solver import model
from . import controls, puzzle, state


class Application(tk.Frame):

    def __init__(self, master: tk.Tk, view_state: state.ViewState):
        super().__init__(master)
        self._state = view_state
        self._puzzle_view: typing.Optional[puzzle.PuzzleView] = None
        self._puzzle_controls: typing.Optional[controls.PuzzleControls] = None
        self._solving_controls: typing.Optional[controls.SolvingControls] = None
        self._save_load_controls: typing.Optional[controls.SaveLoadControls] = None

    def render(self) -> None:
        if self._puzzle_view is not None:
            self._puzzle_view.destroy()
        if self._puzzle_controls is not None:
            self._puzzle_controls.destroy()
        if self._solving_controls is not None:
            self._solving_controls.destroy()
        if self._save_load_controls is not None:
            self._save_load_controls.destroy()

        self.pack(padx=50, pady=30)
        self._puzzle_view = puzzle.PuzzleView(self, view_state=self._state)
        self._state.register_rerender_puzzle_handler(self._puzzle_view.render)
        self._puzzle_view.render()

        self._puzzle_controls = controls.PuzzleControls(self, view_state=self._state)
        self._puzzle_controls.render()
        self._solving_controls = controls.SolvingControls(self, view_state=self._state)
        self._solving_controls.render()
        self._save_load_controls = controls.SaveLoadControls(
            self, view_state=self._state
        )
        self._save_load_controls.render()


def main(puzzle_state: model.PuzzleState) -> None:
    view_state = state.ViewState(puzzle_state=puzzle_state)

    root = tk.Tk()
    app = Application(root, view_state=view_state)
    root.title("Masyu Solver")
    root.geometry("+500+200")
    app.render()
    root.mainloop()
