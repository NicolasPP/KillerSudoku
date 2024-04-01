from pathlib import Path

from pygame import image
from pygame import transform
from pygame.color import Color
from pygame.surface import Surface

from config.app_config import ICONS
from typing import Optional
from pygame.math import Vector2


class AssetManager:

    icons: dict[str, Surface] = {}

    @staticmethod
    def load_icons() -> None:
        for file in Path(ICONS).iterdir():
            if file.is_dir():
                continue

            AssetManager.icons[file.stem] = image.load(file.absolute())

    @staticmethod
    def get_icon(icon: str, background_color: Color, size: Optional[Vector2] = None) -> Surface:
        assert (icon_surface := AssetManager.icons[icon]) is not None

        if size is not None:
            icon_surface = transform.scale(icon_surface, size)

        background: Surface = Surface(icon_surface.get_size())
        background.fill(background_color)
        background.blit(icon_surface, (0, 0))
        return background
