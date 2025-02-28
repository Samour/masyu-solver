import tkinter as tk
from tkinter import filedialog
import typing
from solver import model, serialization
from . import sizeselector


class ChangeSizeButton(tk.Frame):

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


class SaveLoadControls(tk.Frame):

    def __init__(
        self,
        master: tk.Frame,
        puzzle_state: model.PuzzleState,
        on_puzzle_load: typing.Callable[[], None],
    ):
        super().__init__(master)
        self._puzzle_state = puzzle_state
        self._on_puzzle_load = on_puzzle_load
        self._load_button: typing.Optional[tk.Button] = None
        self._save_button: typing.Optional[tk.Button] = None

    def render(self) -> None:
        if self._load_button is not None:
            self._load_button.destroy()
        if self._save_button is not None:
            self._save_button.destroy()

        self._load_button = tk.Button(
            self, text="Load puzzle", command=self._on_load_click
        )
        self._load_button.pack(side="left", padx=5)
        self._save_button = tk.Button(
            self, text="Save puzzle", command=self._on_save_click
        )
        self._save_button.pack(padx=5)
        self.pack(pady=5)

    def _on_load_click(self) -> None:
        fh = filedialog.askopenfile()
        if fh is None:
            return

        with fh:
            new_state = serialization.PuzzleDeserializer(fh).deserialize()
        if new_state is None:
            return
        self._puzzle_state.apply(new_state)
        self._on_puzzle_load()

    def _on_save_click(self) -> None:
        fh = filedialog.asksaveasfile()
        if fh is None:
            return

        with fh:
            serialization.PuzzleSerializer(fh).serialize(self._puzzle_state)
