import tkinter as tk
import typing
from . import puzzle


class Application(tk.Frame):

    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self._puzzle_view: typing.Optional[puzzle.PuzzleView] = None
        self._size_button: typing.Optional[tk.Button] = None

    def render(self) -> None:
        if self._puzzle_view is not None:
            self._puzzle_view.destroy()
        if self._size_button is not None:
            self._size_button.destroy()

        self.pack(padx=50, pady=30)
        self._puzzle_view = puzzle.PuzzleView(self)
        self._puzzle_view.render()

        self._size_button = tk.Button(
            self, text="Change size", command=self._on_changesize
        )
        self._size_button.pack()

    def _on_changesize(self) -> None:
        size_selector = _SizeSelector(self)
        size_selector.render()
        size_selector.grab_set()


class _SizeSelector(tk.Toplevel):

    def __init__(self, master: tk.Frame):
        super().__init__(master)
        self._warning_text: typing.Optional[tk.Label] = None
        self._height_row: typing.Optional[tk.LabelFrame] = None
        self._width_row: typing.Optional[tk.LabelFrame] = None
        self._controls_row: typing.Optional[tk.Frame] = None

    def render(self) -> None:
        if self._warning_text is not None:
            self._warning_text.destroy()
        if self._height_row is not None:
            self._height_row.destroy()
        if self._width_row is not None:
            self._width_row.destroy()
        if self._controls_row is not None:
            self._controls_row.destroy()

        self._warning_text = tk.Label(
            self,
            text="Warning: Changing the board size will reset all elements of the board",
            fg="red",
        )
        self._warning_text.pack()

        self._height_row = tk.LabelFrame(self)
        height_label = tk.Label(self._height_row, text="Height:")
        height_label.pack()
        height_input = tk.Entry(self._height_row)
        height_input.pack()
        self._height_row.pack()

        self._width_row = tk.LabelFrame(self)
        width_label = tk.Label(self._width_row, text="Width:")
        width_label.pack()
        width_input = tk.Entry(self._width_row)
        width_input.pack()
        self._width_row.pack()

        self._controls_row = tk.Frame(self)
        cancel_button = tk.Button(
            self._controls_row, text="Cancel", command=self.destroy
        )
        cancel_button.pack()
        confirm_button = tk.Button(self._controls_row, text="Confirm")
        confirm_button.pack()
        self._controls_row.pack()


def main() -> None:
    root = tk.Tk()
    app = Application(root)
    root.title("Masyu Solver")
    root.geometry("+500+200")
    app.render()
    root.mainloop()
