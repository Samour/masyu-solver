import tkinter as tk
from tkinter import filedialog, messagebox
import typing
from solver import serialization
from . import sizeselector, state


class PuzzleControls(tk.Frame):

    def __init__(self, master: tk.Frame, view_state: state.ViewState):
        super().__init__(master)
        self._state = view_state
        self._edit_mode_buttons: typing.Optional[_EditModeButtons] = None
        self._solve_mode_buttons: typing.Optional[_SolveModeButtons] = None

    def render(self) -> None:
        if self._edit_mode_buttons is not None:
            self._edit_mode_buttons.destroy()
        if self._solve_mode_buttons is not None:
            self._solve_mode_buttons.destroy()

        self._edit_mode_buttons = _EditModeButtons(self, view_state=self._state)
        self._edit_mode_buttons.render()
        self.pack()


class _EditModeButtons(tk.Frame):

    def __init__(self, master: tk.Frame, view_state: state.ViewState):
        super().__init__(master)
        self._state = view_state
        self._size_button: typing.Optional[tk.Button] = None
        self._change_mode_button: typing.Optional[tk.Button] = None

    def render(self) -> None:
        if self._size_button is not None:
            self._size_button.destroy()
        if self._change_mode_button is not None:
            self._change_mode_button.destroy()

        self._size_button = tk.Button(
            self, text="Change size", command=self._on_changesize
        )
        self._size_button.pack(side="left", padx=5)
        self._change_mode_button = tk.Button(self, text="Start solving")
        self._change_mode_button.pack(padx=5)
        self.pack(pady=5)

    def _on_changesize(self) -> None:
        size_selector = sizeselector.SizeSelector(
            self, on_resize=self._on_changesize_confirm
        )
        size_selector.render()
        size_selector.grab_set()

    def _on_changesize_confirm(self, width: int, height: int) -> None:
        self._state.puzzle_state.reset(width, height)
        self._state.rerender_puzzle()


class _SolveModeButtons(tk.Frame):

    def __init__(self, master: tk.Frame):
        super().__init__(master)

    def render(self) -> None:
        pass


class SaveLoadControls(tk.Frame):

    def __init__(
        self,
        master: tk.Frame,
        view_state: state.ViewState,
    ):
        super().__init__(master)
        self._state = view_state
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
            self._show_load_warning()
            return
        self._state.puzzle_state.apply(new_state)
        self._state.rerender_puzzle()

    def _show_load_warning(self) -> None:
        messagebox.showwarning(title="Load error", message="Invalid puzzle file")

    def _on_save_click(self) -> None:
        fh = filedialog.asksaveasfile()
        if fh is None:
            return

        with fh:
            serialization.PuzzleSerializer(fh).serialize(self._state.puzzle_state)
