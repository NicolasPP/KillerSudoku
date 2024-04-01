from queue import Queue
from typing import Optional
from typing import override

from pygame import display
from pygame.event import Event

from events import AppEvent
from events import LaunchGameEvent
from game_gui import BoardDisplay
from game_gui import Tools
from game_gui import TopBar
from killer_sudoku_state import KillerSudokuState
from pages import Page
from puzzle_store import PuzzleDifficulty
from region import Region
from themes import GameTheme


class KillerSudoku(Page):
    @override
    def __init__(self, page_id: int, events: Queue[AppEvent]) -> None:
        super().__init__(page_id, events)
        self._state: KillerSudokuState = KillerSudokuState()
        self._difficulty: Optional[PuzzleDifficulty] = None

        top_bar, body, tools = Region.stack(display.get_surface(), 2, 19, 4)

        self._top_bar: TopBar = TopBar(top_bar, GameTheme.default())
        self._board_display: BoardDisplay = BoardDisplay(body, GameTheme.default(), self._state)
        self._tools: Tools = Tools(tools, GameTheme.default())

    def process_launch_game_event(self, launch_game: LaunchGameEvent) -> None:
        self._state.puzzle = launch_game.puzzle
        self._difficulty = launch_game.difficulty

        self._top_bar.theme = launch_game.theme
        self._tools.theme = launch_game.theme
        self._board_display.theme = launch_game.theme

    @override
    def parse_event(self, game_event: Event) -> None:
        self._top_bar.parse_event(game_event, self.events)

    @override
    def render(self) -> None:
        self._top_bar.render()
        self._board_display.render()
        self._tools.render()

    @override
    def update(self, delta_time: float) -> None:
        pass
