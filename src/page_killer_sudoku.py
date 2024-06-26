from queue import Queue
from typing import Optional
from typing import override

from pygame import BUTTON_LEFT
from pygame import MOUSEBUTTONUP
from pygame import display
from pygame import mouse
from pygame.event import Event
from pygame.math import Vector2
from pygame.surface import Surface

from config.app_config import HOVER_ALPHA
from config.app_config import MAIN_MENU_PAGE
from events import AppEvent
from events import LaunchGameEvent
from events import SetPageEvent
from gui_board import BoardGui
from gui_bottom_bar import BottomBar
from gui_top_bar import TopBar
from killer_sudoku_state import Delete
from killer_sudoku_state import KillerSudokuState
from killer_sudoku_state import Place
from page import Page
from puzzle_store import PuzzleDifficulty
from region import PartitionDirection
from region import Region
from themes import AppTheme


class GameOverMenu:

    def __init__(self, parent: Surface, theme: AppTheme) -> None:
        self._parent: Surface = parent
        self._theme: AppTheme = theme
        self._menu_area: Surface = self._create_menu_area()

    def _create_menu_area(self) -> Surface:
        surface: Surface = Surface(Vector2(self._parent.get_size()) * 0.8)
        surface.fill(self._theme.foreground)
        surface.set_alpha(int(HOVER_ALPHA * 1.5))
        return surface

    def render(self) -> None:
        self._parent.blit(self._menu_area, self._menu_area.get_rect(center=self._parent.get_rect().center))


class KillerSudoku(Page):
    @override
    def parse_event(self, game_event: Event) -> None:
        if self._game_over:
            return

        if game_event.type == MOUSEBUTTONUP:
            if game_event.button == BUTTON_LEFT:
                self._handle_digit_press()
                self._handle_eraser_press()
                self._handle_back_press()
                self._handle_undo_press()
                self._handle_end_selection()
                self._handle_game_over()
                self._board_display.require_redraw = True

        self._bottom_bar.parse_event(game_event, self.events)
        self._board_display.parse_event(game_event, self.events)

    @override
    def render(self) -> None:
        self._top_bar.render()
        self._board_display.render()
        self._bottom_bar.render()

        if self._game_over:
            self._game_over_menu.render()

    @override
    def update(self, delta_time: float) -> None:
        self._board_display.update(delta_time)
        self._top_bar.update(delta_time)

    @override
    def update_theme(self, theme: AppTheme) -> None:
        self._theme = theme
        self._top_bar.theme = theme
        self._bottom_bar.theme = theme
        self._board_display.theme = theme

    def __init__(self, page_id: int, events: Queue[AppEvent], theme: AppTheme) -> None:
        super().__init__(page_id, events, theme)
        self._state: KillerSudokuState = KillerSudokuState()
        self._difficulty: Optional[PuzzleDifficulty] = None

        top_bar, body, tools = Region.partition(display.get_surface(), PartitionDirection.VERTICAL, 3, 21, 6)

        self._top_bar: TopBar = TopBar(top_bar, self._theme)
        self._board_display: BoardGui = BoardGui(body, self._theme, self._state)
        self._bottom_bar: BottomBar = BottomBar(tools, self._theme)
        self._game_over_menu: GameOverMenu = GameOverMenu(display.get_surface(), self._theme)
        self._game_over: bool = False

    def process_launch_game_event(self, launch_game: LaunchGameEvent) -> None:
        self._state.clear()
        self._top_bar.reset_timer()
        self._state.puzzle = launch_game.puzzle
        self._difficulty = launch_game.difficulty
        self._top_bar.begin_timer()

    def _handle_digit_press(self) -> None:
        if (dig := self._bottom_bar.digits.get_collided(self._bottom_bar.get_collision_offset())) is None:
            return

        if dig.is_complete:
            return

        cells: list[tuple[int, int]] = [(cell.row, cell.col) for cell in self._board_display.selection.selected]
        self._state.process_move(Place(cells, self._state, dig.val, self._bottom_bar.tools.pencil.is_on))
        self._bottom_bar.digits.update_digits(self._state, self._theme)

    def _handle_eraser_press(self) -> None:
        if not self._bottom_bar.tools.eraser.is_collided(self._bottom_bar.get_collision_offset()):
            return

        cells: list[tuple[int, int]] = [(cell.row, cell.col) for cell in self._board_display.selection.selected]
        self._state.process_move(Delete(cells, self._state))
        self._bottom_bar.digits.update_digits(self._state, self._theme)

    def _handle_undo_press(self) -> None:
        if not self._bottom_bar.tools.undo.is_collided(self._bottom_bar.get_collision_offset()):
            return

        self._state.undo_move()
        self._bottom_bar.digits.update_digits(self._state, self._theme)

    def _handle_back_press(self) -> None:
        if not self._top_bar.is_back_collided():
            return

        self.events.put(SetPageEvent(MAIN_MENU_PAGE))
        self._board_display.selection.clear()
        self._bottom_bar.digits.reset(self._theme)

    def _handle_end_selection(self) -> None:
        if not self._board_display.parent.placement.collidepoint(mouse.get_pos()):
            return

        self._top_bar.set_selection_sum(self._board_display.selection.get_selection_sum(self._state))

    def _handle_game_over(self) -> None:
        if self._state.is_puzzle_solved():
            self._game_over = True
            self._top_bar.stop_timer()
