import enum
import typing


class LineType(enum.Enum):
    VERTICAL = 1
    HORIZONTAL = 2


class Colours:
    CANVAS_BG = "white"
    DOT = "black"
    CIRCLE_OUTLINE = "black"
    CIRCLE_INNER = "white"
    LINE = "black"


class Coords:
    OFFSET = 2
    TILE_SIZE = 30
    CLICK_PROXIMITY = 10
    LINE_WIDTH = 1

    class Dot:
        RADIUS = 1

        @staticmethod
        def get_rect(x: int, y: int) -> typing.Tuple[float, float, float, float]:
            return Coords._get_rect_for_circle(x, y, Coords.Dot.RADIUS)

    class Circle:
        RADIUS = 5

        @staticmethod
        def get_rect(x: int, y: int) -> typing.Tuple[float, float, float, float]:
            return Coords._get_rect_for_circle(x, y, Coords.Circle.RADIUS)

    @staticmethod
    def _get_rect_for_circle(
        x: int, y: int, radius: int
    ) -> typing.Tuple[float, float, float, float]:
        tile_x = (x + 0.5) * Coords.TILE_SIZE
        tile_y = (y + 0.5) * Coords.TILE_SIZE

        circle_x0 = tile_x - radius + Coords.OFFSET
        circle_x1 = tile_x + radius + Coords.OFFSET
        circle_y0 = tile_y - radius + Coords.OFFSET
        circle_y1 = tile_y + radius + Coords.OFFSET

        return circle_x0, circle_y0, circle_x1, circle_y1

    @staticmethod
    def map_to_tile(x: int, y: int) -> typing.Optional[typing.Tuple[int, int]]:
        tile_x = Coords._map_tile_coord(x)
        tile_y = Coords._map_tile_coord(y)
        return (tile_x, tile_y) if tile_x is not None and tile_y is not None else None

    @staticmethod
    def _map_tile_coord(v: int) -> typing.Optional[int]:
        tile_v = (v - Coords.OFFSET) // Coords.TILE_SIZE
        tile_center = (tile_v + 0.5) * Coords.TILE_SIZE
        delta = abs(v - Coords.OFFSET - tile_center)
        return tile_v if delta < Coords.CLICK_PROXIMITY else None

    @staticmethod
    def map_to_line(
        x: int, y: int
    ) -> typing.Optional[typing.Tuple[LineType, int, int]]:
        hline = Coords._map_to_hline(x, y)
        if hline is not None:
            return LineType.HORIZONTAL, hline[0], hline[1]

        vline = Coords._map_to_vline(x, y)
        if vline is not None:
            return LineType.VERTICAL, vline[0], vline[1]

        return None

    @staticmethod
    def _map_to_hline(x: int, y: int) -> typing.Optional[typing.Tuple[int, int]]:
        line_x = Coords._map_line_coord(x, True)
        line_y = Coords._map_line_coord(y, False)
        return (line_x, line_y) if line_x is not None and line_y is not None else None

    @staticmethod
    def _map_to_vline(x: int, y: int) -> typing.Optional[typing.Tuple[int, int]]:
        line_x = Coords._map_line_coord(x, False)
        line_y = Coords._map_line_coord(y, True)
        return (line_x, line_y) if line_x is not None and line_y is not None else None

    @staticmethod
    def _map_line_coord(v: int, center: bool) -> typing.Optional[int]:
        line_offset = (Coords.TILE_SIZE // 2 if center else 0) + Coords.OFFSET
        line_v = (v - line_offset) // Coords.TILE_SIZE
        center_offset = 1.0 if center else 0.5
        line_center = (line_v + center_offset) * Coords.TILE_SIZE
        delta = abs(v - Coords.OFFSET - line_center)
        return line_v if delta < Coords.CLICK_PROXIMITY else None
