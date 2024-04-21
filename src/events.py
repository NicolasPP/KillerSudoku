from abc import ABC
from enum import Enum
from enum import auto

from puzzle_store import Puzzle
from puzzle_store import PuzzleDifficulty


class AppEventType(Enum):
    SET_PAGE = auto()
    LAUNCH_GAME = auto()


class AppEvent(ABC):

    def __init__(self, event_type: AppEventType) -> None:
        self.type: AppEventType = event_type


class SetPageEvent(AppEvent):

    def __init__(self, page_id: int) -> None:
        super().__init__(AppEventType.SET_PAGE)
        self.page_id: int = page_id


class LaunchGameEvent(AppEvent):

    def __init__(self, difficulty: PuzzleDifficulty, puzzle: Puzzle) -> None:
        super().__init__(AppEventType.LAUNCH_GAME)
        self.difficulty: PuzzleDifficulty = difficulty
        self.puzzle: Puzzle = puzzle
