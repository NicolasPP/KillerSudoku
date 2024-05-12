from itertools import chain
from typing import Optional

from pygame.font import Font
from pygame.font import SysFont
from pygame.font import get_fonts
from pygame.math import Vector2
from pygame.surface import Surface

from config.game_config import DIGIT_FONT_SIZE
from killer_sudoku_state import KillerSudokuState
from region import PartitionDirection
from region import Region
from themes import AppTheme


class Digit:

    def __init__(self, val: int, digit_region: Region) -> None:
        self._filled: int = 0
        self._val: int = val
        self.is_complete: bool = False
        self.region: Region = digit_region

    @property
    def val(self) -> int:
        return self._val

    @val.setter
    def val(self, new_val: int) -> None:
        self._val = new_val

    @val.deleter
    def val(self) -> None:
        del self._val

    def draw_val(self, theme: AppTheme) -> None:
        font: Font = SysFont(get_fonts()[0], DIGIT_FONT_SIZE)
        dig: Surface = font.render(str(self._val), True, theme.foreground,
                                   theme.background)
        self.region.surface.blit(dig, dig.get_rect(center=self.region.surface.get_rect().center))

    def update_is_complete(self, board_val_freq: dict[int, int], theme: AppTheme) -> None:
        if (freq := board_val_freq.get(self._val)) is None:
            return

        self.is_complete = freq >= 9
        if self.is_complete:
            self.region.surface.fill(theme.background)

        else:
            self.draw_val(theme)


class Digits:

    def __init__(self, parent: Region) -> None:
        self.parent: Region = parent
        self.digits: list[Digit] = self._create_digits_input()

    def _create_digits_input(self) -> list[Digit]:
        digits: list[Digit] = []
        for index, region in enumerate(Region.partition(self.parent.surface, PartitionDirection.HORIZONTAL,
                                                        *[1] * 9)):
            digits.append(Digit(index + 1, region))

        return digits

    def render(self, offset: Vector2) -> None:
        for digit in self.digits:
            digit.region.render()

        if (digit := self.get_collided(offset)) is not None:
            if not digit.is_complete:
                digit.region.render_hover()

        self.parent.render()

    def update_digits(self, state: KillerSudokuState, theme: AppTheme) -> None:
        board_val_freq: dict[int, int] = {dig.val: list(chain.from_iterable(state.get_state())).count(dig.val) for dig
                                          in self.digits}

        for digit in self.digits:
            digit.update_is_complete(board_val_freq, theme)

    def reset(self, theme: AppTheme) -> None:
        for digit in self.digits:
            digit.is_complete = False
            digit.draw_val(theme)

    def redraw(self, theme: AppTheme) -> None:
        self.parent.surface.fill(theme.background)
        for digit in self.digits:
            digit.theme = theme
            digit.region.surface.fill(theme.background)
            digit.region.set_hover_color(theme.foreground)
            digit.draw_val(theme)

    def get_collided(self, offset: Vector2) -> Optional[Digit]:
        for digit in self.digits:
            if digit.region.is_collided(offset + Vector2(self.parent.placement.topleft)):
                return digit

        return None
