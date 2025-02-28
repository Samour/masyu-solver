import re
import tkinter as tk
import typing


class SizeSelector(tk.Toplevel):

    def __init__(self, master: tk.Frame):
        super().__init__(master)
        self._frame: typing.Optional[tk.Frame] = None
        self._confirm_button: typing.Optional[tk.Button] = None

        self._width_value: typing.Optional[int] = None
        self._height_value: typing.Optional[int] = None
        self._validate_command = self.register(self._on_validate)

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
        width_label = tk.Label(labels_column, text="Width:")
        width_label.pack()
        height_label = tk.Label(labels_column, text="Height:")
        height_label.pack()
        labels_column.pack(side="left")

        inputs_column = tk.Frame(data_row)
        width_input = tk.Entry(
            inputs_column,
            width=2,
            validate="key",
            validatecommand=(self._validate_command, "w", "%P"),
        )
        width_input.pack()
        height_input = tk.Entry(
            inputs_column,
            width=2,
            validate="key",
            validatecommand=(self._validate_command, "h", "%P"),
        )
        height_input.pack()
        inputs_column.pack(padx=5)
        data_row.pack()

        controls_row = tk.Frame(self._frame)
        cancel_button = tk.Button(controls_row, text="Cancel", command=self.destroy)
        cancel_button.pack(side="left")
        self._confirm_button = tk.Button(
            controls_row, text="Confirm", state="disabled", command=self._on_confirm
        )
        self._confirm_button.pack()
        controls_row.pack()
        self._frame.pack(padx=15, pady=15)

    def _on_validate(self, field: typing.Literal["h", "w"], v: str) -> bool:
        if re.match(r"^\d{0,2}$", v) is None:
            return tk.FALSE

        if len(v) == 0:
            self._update_field(field, None)
            return tk.TRUE

        value = int(v)
        if value > 0:
            self._update_field(field, value)
        else:
            self._update_field(field, None)
        return tk.TRUE

    def _update_field(
        self, field: typing.Literal["h", "w"], value: typing.Optional[int]
    ) -> None:
        if field == "h":
            self._height_value = value
        elif field == "w":
            self._width_value = value

        assert self._confirm_button is not None
        self._confirm_button.configure(
            state=(
                "normal"
                if self._height_value is not None and self._width_value is not None
                else "disabled"
            )
        )

    def _on_confirm(self) -> None:
        print(f"Confirming size ({self._width_value},{self._height_value})")
