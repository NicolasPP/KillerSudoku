from abc import abstractmethod
from queue import Queue

from pygame.event import Event

from events import AppEvent
from region import Region
from themes import AppTheme


class GuiComponent:
    @abstractmethod
    def render(self) -> None:
        pass

    @abstractmethod
    def update(self, delta_time: float) -> None:
        pass

    @abstractmethod
    def update_theme(self) -> None:
        pass

    @abstractmethod
    def parse_event(self, game_event: Event, events: Queue[AppEvent]) -> None:
        pass

    def __init__(self, parent: Region, theme: AppTheme) -> None:
        self.parent: Region = parent
        self._theme: AppTheme = theme

    @property
    def theme(self) -> AppTheme:
        return self._theme

    @theme.deleter
    def theme(self) -> None:
        del self._theme

    @theme.setter
    def theme(self, new_theme: AppTheme) -> None:
        self._theme = new_theme
        self.update_theme()
