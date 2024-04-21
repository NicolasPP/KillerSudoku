from queue import Queue
from typing import override

from pygame import BUTTON_LEFT
from pygame import MOUSEBUTTONUP
from pygame.event import Event
from pygame.math import Vector2

from events import AppEvent
from gui_component import GuiComponent
from gui_digits import Digits
from gui_tools import Tools
from region import PartitionDirection
from region import Region
from themes import AppTheme


class BottomBar(GuiComponent):

    @override
    def render(self) -> None:
        self.tools.render(self.get_collision_offset(), self._theme)
        self.digits.render(self.get_collision_offset())
        self.parent.render()

    @override
    def update(self, delta_time: float) -> None:
        pass

    @override
    def update_theme(self) -> None:
        self.parent.surface.fill(self._theme.background_primary)
        self.digits.redraw(self._theme)
        self.tools.redraw(self._theme)

    @override
    def parse_event(self, game_event: Event, events: Queue[AppEvent]) -> None:
        if game_event.type == MOUSEBUTTONUP:
            if game_event.button == BUTTON_LEFT:
                if self.tools.pencil.is_collided(self.get_collision_offset()):
                    self.tools.pencil.toggle()

    def __init__(self, parent: Region, theme: AppTheme) -> None:
        super().__init__(parent, theme)
        tools_region, input_region = \
            Region.partition(parent.surface, PartitionDirection.VERTICAL, 1, 2)

        self.tools: Tools = Tools(tools_region, self._theme)
        self.digits: Digits = Digits(input_region)

    def get_collision_offset(self) -> Vector2:
        return Vector2(self.parent.placement.topleft)
