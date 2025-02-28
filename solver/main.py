from . import model, view


def main() -> None:
    puzzle_state = model.PuzzleState(5, 5)
    view.main(puzzle_state)


if __name__ == "__main__":
    main()
