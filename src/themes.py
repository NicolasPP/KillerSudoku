from __future__ import annotations

from typing import NamedTuple

from pygame.color import Color

from config.app_config import DARK2_THEME
from config.app_config import DARK_THEME
from config.app_config import LIGHT2_THEME
from config.app_config import LIGHT_THEME


class AppTheme(NamedTuple):

    @staticmethod
    def default() -> AppTheme:
        return Themes.themes[LIGHT2_THEME]

    foreground: Color
    highlight: Color
    invalid: Color
    background: Color


class Themes:
    themes: dict[str, AppTheme] = {
        DARK_THEME: AppTheme(
            Color(255, 255, 255),
            Color(186, 255, 41),
            Color(255, 60, 56),
            Color(0, 0, 0),
        ),
        LIGHT_THEME: AppTheme(
            Color(0, 0, 0),
            Color(186, 255, 41),
            Color(255, 60, 56),
            Color(255, 255, 255),
        ),
        DARK2_THEME: AppTheme(
            Color(87, 226, 229),
            Color(186, 255, 41),
            Color(255, 60, 56),
            Color(21, 49, 49),
        ),
        LIGHT2_THEME: AppTheme(
            Color(180, 184, 171),
            Color(186, 255, 41),
            Color(255, 60, 56),
            Color(40, 75, 99),
        )
    }
