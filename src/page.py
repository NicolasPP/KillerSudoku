from abc import ABC
from abc import abstractmethod
from queue import Queue
from typing import Optional
from typing import Type

from pygame import display
from pygame.event import Event

from events import AppEvent
from themes import AppTheme


class Page(ABC):
    @abstractmethod
    def render(self) -> None:
        pass

    @abstractmethod
    def update(self, delta_time: float) -> None:
        pass

    @abstractmethod
    def parse_event(self, game_event: Event) -> None:
        pass

    @abstractmethod
    def update_theme(self, theme: AppTheme) -> None:
        pass

    def __init__(self, page_id: int, events: Queue[AppEvent], theme: AppTheme) -> None:
        self._id: int = page_id
        self._theme: AppTheme = theme
        self.events: Queue[AppEvent] = events

    def display(self) -> None:
        display.get_surface().fill(self._theme.background_primary)
        self.render()
        display.flip()


class PageManager:

    def __init__(self, events: Queue[AppEvent]) -> None:
        self._pages: dict[int, Page] = {}
        self._current_id: Optional[int] = None
        self._events: Queue[AppEvent] = events

    @property
    def page(self) -> Optional[Page]:
        if self._current_id is None:
            return None

        return self._pages[self._current_id]

    @page.deleter
    def page(self) -> None:
        del self._current_id

    @page.setter
    def page(self, page_id: int) -> None:
        if page_id not in self._pages:
            return

        self._current_id = page_id

    def update_pages_theme(self, theme: AppTheme) -> None:
        for page in self._pages.values():
            page.update_theme(theme)

    def add_page(self, page_id: int, page: Type[Page], theme: AppTheme) -> None:
        self._pages[page_id] = page(page_id, self._events, theme)
