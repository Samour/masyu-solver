import abc
from dataclasses import dataclass
from solver import model


class Message(abc.ABC):
    pass


@dataclass(frozen=True)
class UpdateHLine(Message):
    x: int
    y: int
    state: model.LineState


@dataclass(frozen=True)
class UpdateVLine(Message):
    x: int
    y: int
    state: model.LineState


class SolverCompleted(Message):
    pass
