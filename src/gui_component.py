from abc import abstractmethod
from queue import Queue

from pygame.event import Event

from events import AppEvent
from region import Region
from themes import GameTheme


class GuiComponent:

    def __init__(self, parent: Region, theme: GameTheme) -> None:
        self._parent: Region = parent
        self._theme: GameTheme = theme

    @property
    def theme(self) -> GameTheme:
        return self._theme

    @theme.deleter
    def theme(self) -> None:
        del self._theme

    @theme.setter
    def theme(self, new_theme: GameTheme) -> None:
        self._theme = new_theme
        self.update_theme()

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
