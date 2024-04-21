from __future__ import annotations

from abc import ABC
from itertools import chain
from queue import LifoQueue
from typing import Optional

from puzzle_store import Puzzle

type Board = list[list[int]]
type PencilMarks = list[list[list[int]]]


class Move(ABC):

    def __init__(self, affected_cells: list[tuple[int, int]], state: KillerSudokuState) -> None:
        self.affected_cells: list[tuple[int, int]] = affected_cells
        self.prev_vals: dict[tuple[int, int], int] = {(row, col): state[row][col] for row, col in affected_cells}
        self.prev_marks: dict[tuple[int, int], list[int]] = {
            (row, col): state.get_pencil_markings(row, col).copy() for row, col in affected_cells
        }


class Place(Move):

    def __init__(self, affected_cells: list[tuple[int, int]], state: KillerSudokuState,
                 value: int, is_pencil: bool) -> None:
        super().__init__(affected_cells, state)
        self.value: int = value
        self.is_pencil: bool = is_pencil


class Delete(Move):

    def __init__(self, affected_cells: list[tuple[int, int]], state: KillerSudokuState) -> None:
        super().__init__(affected_cells, state)


class KillerSudokuState:

    def __init__(self) -> None:
        self._puzzle: Optional[Puzzle] = None
        self._board_vals: Board = [[0] * 9 for _ in range(9)]
        self._pencil_marks: PencilMarks = [[[], [], [], [], [], [], [], [], []] for _ in range(9)]
        self._moves: LifoQueue[Move] = LifoQueue()

    def __getitem__(self, index: int) -> list[int]:
        return self._board_vals[index]

    def undo_move(self) -> None:
        if self._moves.empty():
            return

        move: Move = self._moves.get()
        for cell_index, value in move.prev_vals.items():
            row, col = cell_index
            self._board_vals[row][col] = value

        for cell_index, markings in move.prev_marks.items():
            row, col = cell_index
            self._pencil_marks[row][col] = markings

    def process_move(self, move: Move) -> None:
        if isinstance(move, Place):
            self._handle_place(move)

        elif isinstance(move, Delete):
            self._handle_delete(move)

        else:
            raise Exception(f"unrecognised move {type(move)}")

        self._moves.put(move)

    def get_pencil_markings(self, row: int, col: int) -> list[int]:
        return self._pencil_marks[row][col]

    def clear(self) -> None:
        self._board_vals = [[0] * 9 for _ in range(9)]
        for markings in chain.from_iterable(self._pencil_marks):
            markings.clear()

    def _handle_place(self, place: Place) -> None:
        for row, col in place.affected_cells:
            if place.is_pencil:
                self._add_pencil_mark(row, col, place.value)

            else:
                self._board_vals[row][col] = place.value

    def _handle_delete(self, delete: Delete) -> None:
        for row, col in delete.affected_cells:
            cell_val: int = self._board_vals[row][col]
            if cell_val != 0:
                self._board_vals[row][col] = 0

            else:
                self._pencil_marks[row][col].clear()

    def _add_pencil_mark(self, row: int, col: int, mark: int) -> None:
        markings: list[int] = self._pencil_marks[row][col]

        if mark == 0:
            return

        if mark in markings:
            markings.remove(mark)

        else:
            markings.append(mark)
            markings.sort()

        assert 0 <= len(markings) <= 9

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
