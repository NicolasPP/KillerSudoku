from typing import Optional

from puzzle_store import Puzzle

type Board = list[list[int]]


class KillerSudokuState:

    def __init__(self) -> None:
        self._puzzle: Optional[Puzzle] = None
        self._board_vals: Board = [[0] * 9 for _ in range(9)]

    def __getitem__(self, index: int) -> list[int]:
        return self._board_vals[index]

    @property
    def puzzle(self) -> Puzzle:
        assert self._puzzle is not None, "Puzzle has not been set"
        return self._puzzle

    @puzzle.setter
    def puzzle(self, puzzle: Puzzle) -> None:
        self._puzzle = puzzle

    @puzzle.deleter
    def puzzle(self) -> None:
        del self._puzzle
