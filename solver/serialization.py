import typing
from . import model


class PuzzleSerializer:

    def __init__(self, writer: typing.IO[typing.Any]):
        self._wh = writer

    def serialize(self, puzzle: model.PuzzleState) -> None:
        self._write_version()
        self._write_delimiter()
        self._write_dimensions(puzzle)
        self._write_delimiter()
        self._write_vertices(puzzle)

    def _write_delimiter(self) -> None:
        self._wh.write(";")

    def _write_version(self) -> None:
        self._wh.write("v=1")

    def _write_dimensions(self, puzzle: model.PuzzleState) -> None:
        self._wh.write(f"s={puzzle.width}x{puzzle.height}")

    def _write_vertices(self, puzzle: model.PuzzleState) -> None:
        for y in range(puzzle.height):
            for x in range(puzzle.width):
                tile = puzzle.get_tile(x, y)
                assert tile is not None
                self._wh.write(self._map_tile_type(tile))

    def _map_tile_type(self, tile: model.TileType) -> str:
        if tile == model.TileType.ANY:
            return "A"
        elif tile == model.TileType.CORNER:
            return "C"
        elif tile == model.TileType.STRAIGHT:
            return "S"
