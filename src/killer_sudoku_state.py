from typing import Optional

from puzzle_store import Puzzle

type Board = list[list[int]]
type PencilMarks = list[list[list[int]]]


class KillerSudokuState:

    def __init__(self) -> None:
        self._puzzle: Optional[Puzzle] = None
        self._board_vals: Board = [[0] * 9 for _ in range(9)]
        self._pencil_marks: PencilMarks = [[[]] * 9 for _ in range(9)]

    def __getitem__(self, index: int) -> list[int]:
        return self._board_vals[index]

    def add_pencil_mark(self, row: int, col: int, mark: int) -> None:
        self._pencil_marks[row][col].append(mark)

    def clear(self) -> None:
        self._board_vals = [[0] * 9 for _ in range(9)]
        self._pencil_marks = [[[]] * 9 for _ in range(9)]

    @property
    def puzzle(self) -> Puzzle:
        assert self._puzzle is not None, "Puzzle has not been set"
        return self._puzzle

    @puzzle.setter
    def puzzle(self, new_puzzle: Puzzle) -> None:
        self._puzzle = new_puzzle

    @puzzle.deleter
    def puzzle(self) -> None:
        del self._puzzle
