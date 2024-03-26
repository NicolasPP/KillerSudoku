from dataclasses import dataclass
from enum import Enum
from enum import auto
from pathlib import Path
from typing import Optional

PUZZLE_DATA_PATH: str = "data"

type CellIndex = tuple[int, int]
type Cage = tuple[int, list[CellIndex]]


class PuzzleDifficulty(Enum):
    EASY = auto()
    NORMAL = auto()
    HARD = auto()
    EXPERT = auto()
    MASTER = auto()


@dataclass(slots=True, frozen=True, repr=False)
class Puzzle:
    diff: PuzzleDifficulty
    cages: list[Cage]


class PuzzleStore:

    def __init__(self) -> None:
        self._store: dict[PuzzleDifficulty, list[Puzzle]] = {}

    def get_puzzles(self, difficulty: PuzzleDifficulty) -> Optional[list[Puzzle]]:
        return self._store.get(difficulty)

    def load(self) -> None:
        if not (difficulty_folder := Path(PUZZLE_DATA_PATH)).is_dir():
            print(f"path: {difficulty_folder.absolute()} is not a Folder")
            return

        for folder in difficulty_folder.iterdir():
            if not folder.is_dir():
                continue

            self._load_folder(folder)

    def _load_folder(self, puzzle_folder: Path) -> None:
        if not (diff_val := puzzle_folder.stem[-1]).isdigit():
            return
        difficulty: PuzzleDifficulty = PuzzleDifficulty(int(diff_val))

        puzzles: list[Puzzle] = []
        for puzzle_file in puzzle_folder.iterdir():
            if puzzle_file.is_dir():
                continue

            puzzles.append(Puzzle(difficulty, extract_puzzle_cages(puzzle_file)))

        print(len(puzzles))
        self._store[difficulty] = puzzles


def extract_puzzle_cages(puzzle_file: Path) -> list[Cage]:
    cages: list[Cage] = []
    with open(puzzle_file, "r") as file:

        line: str = file.readline()

        while line:
            cage_data: list[str] = line.strip().split()[::-1]

            cage_sum: str = cage_data.pop()
            if not cage_sum.isdigit():
                break
            assert int(cage_sum) <= 45

            cages.append(
                (int(cage_sum), list(map(extract_cell_index, cage_data)))
            )

            line = file.readline()

        return cages


def extract_cell_index(cell_index: str) -> CellIndex:
    row, col = cell_index
    assert row.isdigit() and col.isdigit()
    assert 0 <= int(row) <= 8 and 0 <= int(col) <= 8
    return int(row), int(col)
