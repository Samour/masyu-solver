import typing
from solver import model
from . import positions, validator, vertex


class Solver:

    def __init__(self, puzzle_state: model.PuzzleState):
        self._state = puzzle_state
        self._validator = validator.SolutionValidator(puzzle_state=puzzle_state)
        self._affected = positions.AffectedPositions(puzzle_state=puzzle_state)
        self._positions: set[positions.SolverPosition] = set()
        self._vertex_solvers: list[vertex.VertexSolver] = [
            vertex.FillEmptyEdgesVS(puzzle_state=puzzle_state),
            vertex.OnlyLineOptionVS(puzzle_state=puzzle_state),
            vertex.DeadEndVS(puzzle_state=puzzle_state),
            vertex.StraightLineTileVS(puzzle_state=puzzle_state),
            vertex.CornerNextToStraightTileVS(puzzle_state=puzzle_state),
            vertex.CornerTileVS(puzzle_state=puzzle_state),
        ]

    def solve(self) -> None:
        self._load()

        while True:
            while len(self._positions):
                self._serve()

            if self._validator.is_solved():
                return

            guesses = self._guess_candidates()
            if len(guesses) == 0:
                assert False  # Would need to backtrack in this case

            guess = guesses.pop(0)
            self._apply_guess(guess)

    def _load(self) -> None:
        self._positions = set()
        for y in range(self._state.height):
            for x in range(self._state.width):
                if self._state.get_tile(x, y) != model.TileType.ANY:
                    self._positions.add((x, y))

        for y in range(self._state.height):
            for x in range(self._state.width - 1):
                if self._state.get_hline(x, y) != model.LineState.ANY:
                    self._positions.add((x, y))
                    self._positions.add((x + 1, y))

        for y in range(self._state.height - 1):
            for x in range(self._state.width):
                if self._state.get_vline(x, y) != model.LineState.ANY:
                    self._positions.add((x, y))
                    self._positions.add((x, y + 1))

    def _serve(self) -> None:
        (x, y) = self._positions.pop()
        tile = self._state.get_tile(x, y)
        assert tile is not None
        v = positions.Vertex(puzzle_state=self._state, x=x, y=y)
        if v.is_filled and v.type == model.TileType.ANY:
            return

        for solver in self._vertex_solvers:
            updates = solver.make_updates(v)
            if len(updates) > 0:
                self._positions.update(updates)
                self._positions.add((x, y))
                break

    def _guess_candidates(self) -> list[positions.GuessCandidate]:
        candidates: dict[positions.GuessCandidate, int] = {}
        for y in range(self._state.height):
            for x in range(self._state.width):
                vertex = positions.Vertex(puzzle_state=self._state, x=x, y=y)
                if vertex.is_filled:
                    continue

                for c, p in self._make_guess_candidates(vertex):
                    if c not in candidates or candidates[c] < p:
                        candidates[c] = p

        sorted_candidates = [c for c in candidates]
        sorted_candidates.sort(key=lambda c: candidates[c], reverse=True)
        return sorted_candidates

    def _make_guess_candidates(
        self, vertex: positions.Vertex
    ) -> list[typing.Tuple[positions.GuessCandidate, int]]:
        if vertex.type == model.TileType.CORNER and vertex.count_lines > 0:
            priority = positions.GuessPriority.PARTIAL_CORNER
        elif vertex.type != model.TileType.ANY:
            priority = positions.GuessPriority.UNKNOWN_RESTRICTIVE_TILE
        elif vertex.count_lines > 0:
            priority = positions.GuessPriority.PARTIAL_ANY_TILE
        else:
            priority = positions.GuessPriority.REMAINING

        candidates: list[typing.Tuple[positions.GuessCandidate, int]] = []
        if vertex.line_up == model.LineState.ANY:
            candidates.append(
                (
                    positions.GuessCandidate(
                        direction=positions.LineDirection.VERTICAL,
                        x=vertex.x,
                        y=vertex.y - 1,
                    ),
                    priority,
                )
            )
        if vertex.line_right == model.LineState.ANY:
            candidates.append(
                (
                    positions.GuessCandidate(
                        direction=positions.LineDirection.HORIZONTAL,
                        x=vertex.x,
                        y=vertex.y,
                    ),
                    priority,
                )
            )
        if vertex.line_down == model.LineState.ANY:
            candidates.append(
                (
                    positions.GuessCandidate(
                        direction=positions.LineDirection.VERTICAL,
                        x=vertex.x,
                        y=vertex.y,
                    ),
                    priority,
                )
            )
        if vertex.line_left == model.LineState.ANY:
            candidates.append(
                (
                    positions.GuessCandidate(
                        direction=positions.LineDirection.HORIZONTAL,
                        x=vertex.x - 1,
                        y=vertex.y,
                    ),
                    priority,
                )
            )

        return candidates

    def _apply_guess(self, guess: positions.GuessCandidate) -> None:
        print(f"Making guess {guess}")
        if guess.direction == positions.LineDirection.HORIZONTAL:
            self._state.set_hline(guess.x, guess.y, model.LineState.LINE)
            self._positions.update(self._affected.tiles_for_hline(guess.x, guess.y))
        elif guess.direction == positions.LineDirection.VERTICAL:
            self._state.set_vline(guess.x, guess.y, model.LineState.LINE)
            self._positions.update(self._affected.tiles_for_vline(guess.x, guess.y))
        else:
            assert False  # Avoid a potential infinite loop
