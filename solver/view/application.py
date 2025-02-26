import tkinter as tk
import typing
from . import puzzle


class Application(tk.Frame):

    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self._puzzle_view: typing.Optional[puzzle.PuzzleView] = None

    def render(self) -> None:
        if self._puzzle_view is not None:
            self._puzzle_view.destroy()

        self.pack(padx=50, pady=30)
        self._puzzle_view = puzzle.PuzzleView(self)
        self._puzzle_view.render()


def main() -> None:
    root = tk.Tk()
    app = Application(root)
    root.title("Masyu Solver")
    root.geometry("+500+200")
    app.render()
    root.mainloop()
