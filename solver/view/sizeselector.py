import re
import tkinter as tk
import typing


class SizeSelector(tk.Toplevel):

    def __init__(self, master: tk.Frame):
        super().__init__(master)
        self._frame: typing.Optional[tk.Frame] = None

        self._validate_command = self.register(self._on_validate), "%P"

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
        height_input = tk.Entry(
            inputs_column,
            width=2,
            validate="key",
            validatecommand=self._validate_command,
        )
        height_input.pack()
        width_input = tk.Entry(
            inputs_column, width=2, validatecommand=self._validate_command
        )
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

    def _on_validate(self, v: str) -> bool:
        return tk.TRUE if re.match(r"^\d{0,2}$", v) is not None else tk.FALSE
