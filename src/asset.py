from pathlib import Path

from pygame import image
from pygame import transform
from pygame.color import Color
from pygame.surface import Surface

from config.app_config import DEFAULT_ICON_SIZE
from config.app_config import ICONS


class AssetManager:

    icons: dict[str, Surface] = {}

    @staticmethod
    def load_icons() -> None:
        for file in Path(ICONS).iterdir():
            if file.is_dir():
                continue

            AssetManager.icons[file.stem] = transform.scale(image.load(file.absolute()),
                                                            (DEFAULT_ICON_SIZE, DEFAULT_ICON_SIZE))

    @staticmethod
    def get_icon(icon: str, background_color: Color) -> Surface:
        assert (icon_surface := AssetManager.icons[icon]) is not None

        background: Surface = Surface(icon_surface.get_size())
        background.fill(background_color)
        background.blit(icon_surface, (0, 0))
        return background
