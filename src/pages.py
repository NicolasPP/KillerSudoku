from abc import ABC
from abc import abstractmethod
from queue import Queue
from typing import Optional
from typing import Type

from pygame import display
from pygame.color import Color
from pygame.event import Event

from events import AppEvent


class Page(ABC):
    def __init__(self, page_id: int, events: Queue[AppEvent]) -> None:
        self._id: int = page_id
        self._clear_color: Color = Color(255, 255, 255, 0)
        self.events: Queue[AppEvent] = events

    @property
    def clear_color(self) -> Color:
        return self._clear_color

    @clear_color.deleter
    def clear_color(self) -> None:
        del self._clear_color

    @clear_color.setter
    def clear_color(self, color: Color) -> None:
        self._clear_color = color

    def display(self) -> None:
        display.get_surface().fill(self._clear_color)
        self.render()
        display.flip()

    @abstractmethod
    def parse_event(self, game_event: Event) -> None:
        pass

    @abstractmethod
    def render(self) -> None:
        pass

    @abstractmethod
    def update(self, delta_time: float) -> None:
        pass


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

    def add_page(self, page_id: int, page: Type[Page]) -> None:
        self._pages[page_id] = page(page_id, self._events)
