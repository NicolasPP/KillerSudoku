from queue import Queue
from typing import Optional
from typing import override

from pygame.event import Event
from pygame.font import Font
from pygame.font import SysFont
from pygame.font import get_fonts
from pygame.math import Vector2
from pygame.surface import Surface

from config.game_config import DIGIT_FONT_SIZE
from events import AppEvent
from gui_component import GuiComponent
from region import PartitionDirection
from region import Region
from themes import GameTheme


class Digit:

    def __init__(self, val: int, region: Region, theme: GameTheme) -> None:
        self._filled: int = 0
        self._val: int = val
        self._theme: GameTheme = theme
        self.region: Region = region

    @property
    def val(self) -> int:
        return self._val

    @val.setter
    def val(self, new_val: int) -> None:
        self._val = new_val

    @val.deleter
    def val(self) -> None:
        del self._val

    def draw_val(self) -> None:
        font: Font = SysFont(get_fonts()[0], DIGIT_FONT_SIZE)
        dig: Surface = font.render(str(self._val), True, self._theme.foreground_primary,
                                   self._theme.background_primary)
        self.region.surface.blit(dig, dig.get_rect(center=self.region.surface.get_rect().center))


class DigitsGui(GuiComponent):

    @override
    def render(self) -> None:
        for digit in self._digits:
            digit.region.render()

    @override
    def update(self, delta_time: float) -> None:
        pass

    @override
    def update_theme(self) -> None:
        for digit in self._digits:
            digit.region.surface.fill(self._theme.background_primary)
            digit.region.set_hover_color(self._theme.foreground_primary)
            digit.draw_val()

    @override
    def parse_event(self, game_event: Event, events: Queue[AppEvent]) -> None:
        pass

    def __init__(self, parent: Region, theme: GameTheme) -> None:
        super().__init__(parent, theme)
        self._digits: list[Digit] = self._create_digits_input()

    def _create_digits_input(self) -> list[Digit]:
        digits: list[Digit] = []
        for index, region in enumerate(Region.partition(self.parent.surface, PartitionDirection.HORIZONTAL,
                                                        *[1] * 9)):
            digits.append(Digit(index + 1, region, self._theme))

        return digits

    def get_collided(self, offset: Vector2) -> Optional[Digit]:
        for digit in self._digits:
            if digit.region.is_collided(offset):
                return digit

        return None
