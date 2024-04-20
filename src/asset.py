from itertools import product
from pathlib import Path
from typing import Optional

from pygame import image
from pygame import transform
from pygame.color import Color
from pygame.math import Vector2
from pygame.surface import Surface

from config.app_config import ICONS


class AssetManager:

    icons: dict[str, Surface] = {}

    @staticmethod
    def load_icons() -> None:
        for file in Path(ICONS).iterdir():
            if file.is_dir():
                continue

            AssetManager.icons[file.stem] = image.load(file.absolute())

    @staticmethod
    def get_icon(icon_name: str, foreground: Color, background: Color, size: Optional[Vector2] = None) -> Surface:
        assert (icon_surface := AssetManager.icons[icon_name]) is not None

        if size is not None:
            icon_surface = transform.scale(icon_surface, size)

        original_color: Color = Color(0, 0, 0)
        for index in product(range(icon_surface.get_width()), range(icon_surface.get_height())):
            if icon_surface.get_at(index) == original_color:
                icon_surface.set_at(index, foreground)

        icon: Surface = Surface(icon_surface.get_size())
        icon.fill(background)
        icon.blit(icon_surface, (0, 0))
        return icon
