from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from enum import auto

from config.app_config import JSON_PUZZLES

type CellIndex = tuple[int, int]
type Cage = tuple[int, list[CellIndex]]


class PuzzleDifficulty(Enum):
    EASY = auto()
    NORMAL = auto()
    HARD = auto()
    EXPERT = auto()
    MASTER = auto()


@dataclass(slots=True, frozen=True)
class Puzzle:
    volume: int
    book: int
    id: int
    diff: PuzzleDifficulty
    cages: list[Cage]


class PuzzleStore:
    _store: dict[PuzzleDifficulty, list[Puzzle]] = {}

    @staticmethod
    def get_puzzles(difficulty: PuzzleDifficulty) -> list[Puzzle]:
        return PuzzleStore._store.get(difficulty, [])

    @staticmethod
    def load_puzzles() -> None:
        with open(JSON_PUZZLES, "r") as file:
            for puzzle_data in json.load(file):
                diff: PuzzleDifficulty = PuzzleDifficulty[puzzle_data["diff"]]
                cages: list[Cage] = []

                for cage_sum, cage_cells in puzzle_data["cages"]:
                    cells: list[tuple[int, int]] = []
                    for row, col in cage_cells:
                        cells.append((int(row), int(col)))

                    cages.append((int(cage_sum), cells))

                puzzle: Puzzle = Puzzle(puzzle_data["volume"], puzzle_data["book"], puzzle_data["id"], diff, cages)

                if diff not in PuzzleStore._store:
                    PuzzleStore._store[diff] = []

                PuzzleStore._store[diff].append(puzzle)
