import typing
from . import model


class _Symbols:
    DELIM = ";"
    VERSION_PREFIX = "v="
    DIMENSIONS_PREFIX = "s="
    DIMENSIONS_DELIM = "x"

    class TileType:
        ANY = "A"
        CORDER = "C"
        STRAIGHT = "S"


class PuzzleSerializer:

    _VERSION = 1

    def __init__(self, writer: typing.IO[typing.Any]):
        assert writer.writable()
        self._wh = writer

    def serialize(self, puzzle: model.PuzzleState) -> None:
        self._write_version()
        self._write_delimiter()
        self._write_dimensions(puzzle)
        self._write_delimiter()
        self._write_vertices(puzzle)

    # Adding this just to get the type hint
    def _write(self, data: str) -> None:
        self._wh.write(data)

    def _write_delimiter(self) -> None:
        self._write(_Symbols.DELIM)

    def _write_version(self) -> None:
        self._write(_Symbols.VERSION_PREFIX)
        self._write(str(self._VERSION))

    def _write_dimensions(self, puzzle: model.PuzzleState) -> None:
        self._write(_Symbols.DIMENSIONS_PREFIX)
        self._write(str(puzzle.width))
        self._write(_Symbols.DIMENSIONS_DELIM)
        self._write(str(puzzle.height))

    def _write_vertices(self, puzzle: model.PuzzleState) -> None:
        for y in range(puzzle.height):
            for x in range(puzzle.width):
                tile = puzzle.get_tile(x, y)
                assert tile is not None
                self._write(self._map_tile_type(tile))

    def _map_tile_type(self, tile: model.TileType) -> str:
        if tile == model.TileType.ANY:
            return _Symbols.TileType.ANY
        elif tile == model.TileType.CORNER:
            return _Symbols.TileType.CORDER
        elif tile == model.TileType.STRAIGHT:
            return _Symbols.TileType.STRAIGHT
