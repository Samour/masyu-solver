from . import model
from .view import application


def main() -> None:
    puzzle_state = model.PuzzleState(5, 5)
    application.main(puzzle_state)


if __name__ == "__main__":
    main()
