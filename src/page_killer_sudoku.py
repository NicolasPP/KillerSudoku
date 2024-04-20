from queue import Queue
from typing import Optional
from typing import override

from pygame import BUTTON_LEFT
from pygame import MOUSEBUTTONDOWN
from pygame import display
from pygame.event import Event

from config.app_config import MAIN_MENU_PAGE
from events import AppEvent
from events import LaunchGameEvent
from events import SetPageEvent
from gui_board import BoardGui
from gui_bottom_bar import BottomBar
from gui_top_bar import TopBar
from killer_sudoku_state import KillerSudokuState
from page import Page
from puzzle_store import PuzzleDifficulty
from region import PartitionDirection
from region import Region
from themes import GameTheme


class KillerSudoku(Page):
    @override
    def parse_event(self, game_event: Event) -> None:
        self._board_display.parse_event(game_event, self.events)

        if game_event.type == MOUSEBUTTONDOWN:
            if game_event.button == BUTTON_LEFT:
                self._handle_digit_press()
                self._handle_eraser_press()
                self._handle_back_press()

    @override
    def render(self) -> None:
        self._top_bar.render()
        self._board_display.render()
        self._bottom_bar.render()

    @override
    def update(self, delta_time: float) -> None:
        pass

    def __init__(self, page_id: int, events: Queue[AppEvent]) -> None:
        super().__init__(page_id, events)
        self._state: KillerSudokuState = KillerSudokuState()
        self._difficulty: Optional[PuzzleDifficulty] = None

        top_bar, body, tools = Region.partition(display.get_surface(), PartitionDirection.VERTICAL, 2, 19, 4)

        self._top_bar: TopBar = TopBar(top_bar, GameTheme.default())
        self._board_display: BoardGui = BoardGui(body, GameTheme.default(), self._state)
        self._bottom_bar: BottomBar = BottomBar(tools, GameTheme.default())

    def process_launch_game_event(self, launch_game: LaunchGameEvent) -> None:
        self._state.clear()
        self._state.puzzle = launch_game.puzzle
        self._difficulty = launch_game.difficulty

        self._top_bar.theme = launch_game.theme
        self._bottom_bar.theme = launch_game.theme
        self._board_display.theme = launch_game.theme

    def _handle_digit_press(self) -> None:
        if (dig := self._bottom_bar.digits.get_collided(self._bottom_bar.get_collision_offset())) is None:
            return

        if self._board_display.selected is None:
            return

        self._state[self._board_display.selected.row][self._board_display.selected.col] = dig.val
        self._board_display.require_redraw = True

    def _handle_eraser_press(self) -> None:
        if not self._bottom_bar.tools.eraser.is_collided(self._bottom_bar.get_collision_offset()):
            return

        if self._board_display.selected is None:
            return

        self._state[self._board_display.selected.row][self._board_display.selected.col] = 0
        self._board_display.require_redraw = True

    def _handle_back_press(self) -> None:
        if not self._top_bar.is_back_collided():
            return

        self.events.put(SetPageEvent(MAIN_MENU_PAGE))
        self._board_display.require_redraw = True
