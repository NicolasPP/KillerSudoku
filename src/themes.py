from __future__ import annotations

from typing import NamedTuple

from pygame.color import Color

from config.app_config import DARK2_THEME
from config.app_config import DARK_THEME
from config.app_config import LIGHT_THEME


class AppTheme(NamedTuple):

    @staticmethod
    def default() -> AppTheme:
        return Themes.themes[DARK2_THEME]

    foreground_primary: Color
    foreground_secondary: Color
    background_primary: Color
    background_secondary: Color


class Themes:
    themes: dict[str, AppTheme] = {
        DARK_THEME: AppTheme(
            Color(255, 255, 255),
            Color(255, 255, 255),
            Color(0, 0, 0),
            Color(0, 0, 0),
        ),
        LIGHT_THEME: AppTheme(
            Color(0, 0, 0),
            Color(0, 0, 0),
            Color(255, 255, 255),
            Color(255, 255, 255),
        ),
        DARK2_THEME: AppTheme(
            Color(87, 226, 229),
            Color(87, 226, 229),
            Color(21, 49, 49),
            Color(21, 49, 49),
        )
    }
