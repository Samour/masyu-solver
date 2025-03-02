import typing
from solver import model
from . import positions, validator, vertex


class Solver:

    def __init__(self, puzzle_state: model.PuzzleState):
        self._state = puzzle_state
        self._validator = validator.SolutionValidator(puzzle_state=puzzle_state)
        self._affected = positions.AffectedPositions(puzzle_state=puzzle_state)
        self._positions: set[positions.SolverPosition] = set()
        self._backtrack_states: list[
            typing.Tuple[model.PuzzleState, positions.GuessCandidate]
        ] = []
        self._vertex_solvers: list[vertex.VertexSolver] = [
            vertex.FillEmptyEdgesVS(puzzle_state=puzzle_state),
            vertex.OnlyLineOptionVS(puzzle_state=puzzle_state),
            vertex.DeadEndVS(puzzle_state=puzzle_state),
            vertex.StraightLineTileVS(puzzle_state=puzzle_state),
            vertex.CornerNextToStraightTileVS(puzzle_state=puzzle_state),
            vertex.ConsecutiveStraightTilesVS(puzzle_state=puzzle_state),
            vertex.CornerTileVS(puzzle_state=puzzle_state),
        ]

    def solve(self) -> None:
        self._load()

        while True:
            while len(self._positions):
                if not self._serve():
                    self._backtrack()

            solution_state = self._validator.is_solved()
            if solution_state == validator.SolutionValue.SOLVED:
                return
            elif solution_state == validator.SolutionValue.INVALID:
                self._backtrack()
                continue

            guesses = self._guess_candidates()
            if len(guesses) == 0:
                self._backtrack()
            else:
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

    def _serve(self) -> bool:
        (x, y) = self._positions.pop()
        tile = self._state.get_tile(x, y)
        assert tile is not None
        v = positions.Vertex(puzzle_state=self._state, x=x, y=y)
        if v.is_filled and v.type == model.TileType.ANY:
            return True

        for solver in self._vertex_solvers:
            updates = solver.make_updates(v)
            if len(updates) > 0:
                for (u_x, u_y) in updates:
                    if not self._check_node(u_x, u_y):
                        return False
                self._positions.update(updates)
                self._positions.add((x, y))
                break

        return True
    
    def _check_node(self, x: int, y: int) -> bool:
        if self._validator.validate_vertex(x, y) == validator.SolutionValue.INVALID:
            return False
        walk_length = self._validator.walk_nodes(x, y)
        if walk_length is None:
            return True
        
        return self._validator.discover_lines() == walk_length

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
        snapshot = model.PuzzleState(1, 1)
        snapshot.apply(self._state)
        self._backtrack_states.append((snapshot, guess))

        if guess.direction == positions.LineDirection.HORIZONTAL:
            self._state.set_hline(guess.x, guess.y, model.LineState.LINE)
            self._positions.update(self._affected.tiles_for_hline(guess.x, guess.y))
        elif guess.direction == positions.LineDirection.VERTICAL:
            self._state.set_vline(guess.x, guess.y, model.LineState.LINE)
            self._positions.update(self._affected.tiles_for_vline(guess.x, guess.y))
        else:
            assert False  # Avoid a potential infinite loop

    def _backtrack(self) -> None:
        snapshot, guess = self._backtrack_states.pop()
        self._state.apply(snapshot)
        self._positions = set()

        if guess.direction == positions.LineDirection.HORIZONTAL:
            self._state.set_hline(guess.x, guess.y, model.LineState.EMPTY)
            self._positions.update(self._affected.tiles_for_hline(guess.x, guess.y))
        elif guess.direction == positions.LineDirection.VERTICAL:
            self._state.set_vline(guess.x, guess.y, model.LineState.EMPTY)
            self._positions.update(self._affected.tiles_for_vline(guess.x, guess.y))
