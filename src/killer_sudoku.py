from queue import Queue
from typing import Optional
from typing import override

from pygame.event import Event

from events import AppEvent
from pages import Page
from puzzle_store import Puzzle
from puzzle_store import PuzzleDifficulty
from themes import GameTheme


class KillerSudokuState:

    def __init__(self) -> None:
        self._puzzle: Optional[Puzzle] = None

    def set_puzzle(self, puzzle: Puzzle) -> None:
        self._puzzle = puzzle

    def get_puzzle(self) -> Puzzle:
        assert self._puzzle is not None, "Puzzle has not been set"
        return self._puzzle


class KillerSudoku(Page):
    @override
    def __init__(self, page_id: int, events: Queue[AppEvent]) -> None:
        super().__init__(page_id, events)
        self._state: KillerSudokuState = KillerSudokuState()
        self.difficulty: Optional[PuzzleDifficulty] = None
        self.theme: Optional[GameTheme] = None

    def set_puzzle_info(self, difficulty: PuzzleDifficulty, puzzle: Puzzle, theme: GameTheme) -> None:
        self._state.set_puzzle(puzzle)
        self.difficulty = difficulty
        self.theme = theme

    @override
    def parse_event(self, game_event: Event) -> None:
        pass

    @override
    def render(self) -> None:
        pass

    @override
    def update(self, delta_time: float) -> None:
        pass
