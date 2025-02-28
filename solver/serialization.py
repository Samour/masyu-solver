import re
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

    class LineState:
        ANY = "A"
        LINE = "L"
        EMPTY = "E"


class PuzzleSerializer:

    _VERSION = 2

    def __init__(self, writer: typing.IO[typing.Any]):
        assert writer.writable()
        self._wh = writer

    def serialize(self, puzzle: model.PuzzleState) -> None:
        self._write_version()
        self._write_delimiter()
        self._write_dimensions(puzzle)
        self._write_delimiter()
        self._write_vertices(puzzle)
        self._write_delimiter()
        self._write_hlines(puzzle)
        self._write_delimiter()
        self._write_vlines(puzzle)

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

    def _write_hlines(self, puzzle: model.PuzzleState) -> None:
        for y in range(puzzle.height):
            for x in range(puzzle.width - 1):
                line = puzzle.get_hline(x, y)
                assert line is not None
                self._write(self._map_line_state(line))

    def _write_vlines(self, puzzle: model.PuzzleState) -> None:
        for y in range(puzzle.height - 1):
            for x in range(puzzle.width):
                line = puzzle.get_vline(x, y)
                assert line is not None
                self._write(self._map_line_state(line))

    def _map_line_state(self, line: model.LineState) -> str:
        if line == model.LineState.ANY:
            return _Symbols.LineState.ANY
        elif line == model.LineState.LINE:
            return _Symbols.LineState.LINE
        elif line == model.LineState.EMPTY:
            return _Symbols.LineState.EMPTY


class PuzzleDeserializer:

    _VERSION = 2

    def __init__(self, reader: typing.IO[typing.Any]):
        assert reader.readable()
        self._rh = reader

    def deserialize(self) -> typing.Optional[model.PuzzleState]:
        if not self._read_validate_version():
            return None

        dimensions = self._read_dimensions()
        if dimensions is None:
            return None

        width, height = dimensions
        puzzle_state = model.PuzzleState(width=width, height=height)

        return (
            puzzle_state
            if self._read_vertices(puzzle_state)
            and self._read_hlines(puzzle_state)
            and self._read_vlines(puzzle_state)
            else None
        )

    def _read_section(self) -> typing.Optional[str]:
        section: list[str] = []
        c = self._rh.read(1)
        if not len(c):
            return None

        while len(c) and c != _Symbols.DELIM:
            section.append(c)
            c = self._rh.read(1)

        return "".join(section)

    def _read_validate_version(self) -> bool:
        version_section = self._read_section()
        if version_section is None:
            print("ERROR: File is empty")
            return False

        version = self._parse_version(version_section)
        if version is None:
            print("ERROR: Could not parse version")
            return False
        elif version != self._VERSION:
            print(f"ERROR: Invalid version {version}")
            return False

        return True

    def _parse_version(self, data: str) -> typing.Optional[int]:
        match = re.match(f"^{_Symbols.VERSION_PREFIX}(\\d)+$", data)
        return int(match.group(1)) if match is not None else None

    def _read_dimensions(self) -> typing.Optional[typing.Tuple[int, int]]:
        dimensions_section = self._read_section()
        if dimensions_section is None:
            print("ERROR: Unexpected end of file while trying to read dimensions")
            return None

        dimensions = re.match(
            f"^{_Symbols.DIMENSIONS_PREFIX}(\\d+){_Symbols.DIMENSIONS_DELIM}(\\d+)$",
            dimensions_section,
        )
        if dimensions is None:
            print("ERROR: Could not parse dimensions")
            return None

        return int(dimensions.group(1)), int(dimensions.group(2))

    def _read_vertices(self, puzzle_state: model.PuzzleState) -> bool:
        vertices_section = self._read_section()
        if vertices_section is None:
            print("ERROR: Unexpected end of file while trying to read vertices")
            return False

        x = 0
        y = 0
        for c in vertices_section:
            tile_type = self._map_tile_type(c)
            if tile_type is None:
                print(f"ERROR: Unexpected vertex type at ({x}, {y})")
                return False
            try:
                puzzle_state.set_tile(x, y, tile_type)
            except:
                print(f"ERROR: Invalid coordinates ({x}, {y})")
                return False
            x += 1
            if x >= puzzle_state.width:
                x = 0
                y += 1

        return True

    def _map_tile_type(self, data: str) -> typing.Optional[model.TileType]:
        if data == _Symbols.TileType.ANY:
            return model.TileType.ANY
        elif data == _Symbols.TileType.CORDER:
            return model.TileType.CORNER
        elif data == _Symbols.TileType.STRAIGHT:
            return model.TileType.STRAIGHT
        else:
            return None

    def _read_hlines(self, puzzle_state: model.PuzzleState) -> bool:
        hlines_section = self._read_section()
        if hlines_section is None:
            print("ERROR: Unexpected end of file while trying to read hlines")
            return False

        x = 0
        y = 0
        for c in hlines_section:
            line_state = self._map_line_state(c)
            if line_state is None:
                print(f"ERROR: Unexpected line type at ({x}, {y})")
                return False
            try:
                puzzle_state.set_hline(x, y, line_state)
            except:
                print(f"ERROR: Invalid coordinates ({x}, {y})")
                return False
            x += 1
            if x >= puzzle_state.width - 1:
                x = 0
                y += 1

        return True

    def _read_vlines(self, puzzle_state: model.PuzzleState) -> bool:
        vlines_section = self._read_section()
        if vlines_section is None:
            print("ERROR: Unexpected end of file while trying to read vlines")
            return False

        x = 0
        y = 0
        for c in vlines_section:
            line_state = self._map_line_state(c)
            if line_state is None:
                print(f"ERROR: Unexpected line type at ({x}, {y})")
                return False
            try:
                puzzle_state.set_vline(x, y, line_state)
            except:
                print(f"ERROR: Invalid coordinates ({x}, {y})")
                return False
            x += 1
            if x >= puzzle_state.width:
                x = 0
                y += 1

        return True

    def _map_line_state(self, data: str) -> typing.Optional[model.LineState]:
        if data == _Symbols.LineState.ANY:
            return model.LineState.ANY
        elif data == _Symbols.LineState.LINE:
            return model.LineState.LINE
        elif data == _Symbols.LineState.EMPTY:
            return model.LineState.EMPTY
        else:
            return None
