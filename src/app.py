from queue import Queue
from typing import Optional

import pygame

from asset import AssetManager
from config.app_config import APP_HEIGHT
from config.app_config import APP_WIDTH
from config.app_config import KILLER_SUDOKU_PAGE
from config.app_config import MAIN_MENU_PAGE
from config.app_config import MAX_PUZZLES
from delta_time import DeltaTime
from events import AppEvent
from events import LaunchGameEvent
from events import SetPageEvent
from page import Page
from page import PageManager
from page_killer_sudoku import KillerSudoku
from page_main_menu import MainMenu
from puzzle_store import PuzzleStore
from themes import AppTheme


class KillerSudokuApp:

    def __init__(self) -> None:

        self._app_events: Queue[AppEvent] = Queue()
        self._theme: AppTheme = AppTheme.default()
        self._page_manager: PageManager = PageManager(self._app_events)
        self._delta_time: DeltaTime = DeltaTime()
        self._is_done: bool = False

        pygame.init()
        PuzzleStore.load_puzzles(MAX_PUZZLES)
        pygame.display.set_mode((APP_WIDTH, APP_HEIGHT))
        AssetManager.load_icons()

        self._page_manager.add_page(MAIN_MENU_PAGE, MainMenu, self._theme)
        self._page_manager.add_page(KILLER_SUDOKU_PAGE, KillerSudoku, self._theme)
        self._page_manager.page = MAIN_MENU_PAGE

        self._page_manager.update_pages_theme(self._theme)

    def play(self) -> None:
        while not self._is_done:

            self._delta_time.set()
            self._parse_app_events()

            if (page := self._page_manager.page) is None:
                continue

            page.update(self._delta_time.get())
            page.display()

            self._forward_game_events(page)

    def _forward_game_events(self, page: Page) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._is_done = True
            else:
                page.parse_event(event)

    def _parse_app_events(self) -> None:
        while not self._app_events.empty():

            app_event: AppEvent = self._app_events.get()

            if isinstance(app_event, SetPageEvent):
                self._page_manager.page = app_event.page_id

            elif isinstance(app_event, LaunchGameEvent):
                self._page_manager.page = KILLER_SUDOKU_PAGE
                page: Optional[Page] = self._page_manager.page
                assert isinstance(page, KillerSudoku)
                page.process_launch_game_event(app_event)

            else:
                raise Exception(f"App Event: {app_event.type.name} not recognised")
