from queue import Queue
from typing import override

from pygame.event import Event

from events import AppEvent
from gui_component import GuiComponent
from region import Region
from themes import GameTheme


class Tools(GuiComponent):

    def __init__(self, parent: Region, theme: GameTheme) -> None:
        super().__init__(parent, theme)

    @override
    def render(self) -> None:
        pass

    @override
    def parse_event(self, game_event: Event, events: Queue[AppEvent]) -> None:
        pass

    @override
    def update(self, delta_time: float) -> None:
        pass

    @override
    def update_theme(self) -> None:
        self._parent.surface.fill(self._theme.background_primary)
