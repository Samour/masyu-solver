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
        self._frame: typing.Optional[tk.Frame] = None

    def render(self) -> None:
        if self._frame is not None:
            self._frame.destroy()

        self._frame = tk.Frame(self)
        warning_row = tk.Frame(self._frame)
        warning_label = tk.Label(
            warning_row,
            text="Warning:",
            fg="red",
        )
        warning_label.pack(side="left")
        warning_message = tk.Label(
            warning_row,
            text="Changing the board size will reset all elements of the board",
        )
        warning_message.pack()
        warning_row.pack()

        data_row = tk.Frame(self._frame)
        labels_column = tk.Frame(data_row)
        height_label = tk.Label(labels_column, text="Height:")
        height_label.pack()
        width_label = tk.Label(labels_column, text="Width:")
        width_label.pack()
        labels_column.pack(side="left")

        inputs_column = tk.Frame(data_row)
        height_input = tk.Entry(inputs_column, width=2)
        height_input.pack()
        width_input = tk.Entry(inputs_column, width=2)
        width_input.pack()
        inputs_column.pack(padx=5)
        data_row.pack()

        controls_row = tk.Frame(self._frame)
        cancel_button = tk.Button(controls_row, text="Cancel", command=self.destroy)
        cancel_button.pack(side="left")
        confirm_button = tk.Button(controls_row, text="Confirm")
        confirm_button.pack()
        controls_row.pack()
        self._frame.pack(padx=15, pady=15)


def main() -> None:
    root = tk.Tk()
    app = Application(root)
    root.title("Masyu Solver")
    root.geometry("+500+200")
    app.render()
    root.mainloop()
