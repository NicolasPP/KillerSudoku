from queue import Queue
from typing import override

from pygame.event import Event
from pygame.math import Vector2

from events import AppEvent
from gui_component import GuiComponent
from gui_digits import DigitsGui
from region import PartitionDirection
from region import Region
from themes import GameTheme


class Tools(GuiComponent):

    @override
    def render(self) -> None:
        self._tools_region.render()

        self._digits.render()

        if (digit := self._digits.get_collided(self.get_digit_collision_offset())) is not None:
            digit.region.render_hover()

        self._digits.parent.render()

        self.parent.render()

    @override
    def update(self, delta_time: float) -> None:
        pass

    @override
    def update_theme(self) -> None:
        self._tools_region.surface.fill(self._theme.background_primary)
        self._input_region.surface.fill(self._theme.background_primary)
        self.parent.surface.fill(self._theme.background_primary)

    @override
    def parse_event(self, game_event: Event, events: Queue[AppEvent]) -> None:
        pass

    def __init__(self, parent: Region, theme: GameTheme) -> None:
        super().__init__(parent, theme)
        self._tools_region, self._input_region = \
            Region.partition(parent.surface, PartitionDirection.VERTICAL, 1, 2)

        self._digits: DigitsGui = DigitsGui(self._input_region, self._theme)

    @property
    def digits(self) -> DigitsGui:
        return self._digits

    @digits.deleter
    def digits(self) -> None:
        del self._digits

    @digits.setter
    def digits(self, new_digit: DigitsGui) -> None:
        self._digits = new_digit

    def get_digit_collision_offset(self) -> Vector2:
        return Vector2(self.parent.placement.topleft) + Vector2(self._digits.parent.placement.topleft)
