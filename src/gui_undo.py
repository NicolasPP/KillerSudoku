from pygame import mouse
from pygame.math import Vector2
from pygame.surface import Surface

from asset import AssetManager
from config.app_config import HOVER_ALPHA
from config.app_config import UNDO_ICON
from region import Region
from themes import AppTheme


class Undo:

    def __init__(self, parent: Region, theme: AppTheme) -> None:
        self.parent: Region = parent
        self._icon: Surface = self._get_icon(theme)

    def redraw(self, theme: AppTheme) -> None:
        self.parent.surface.fill(theme.background)
        self._icon = self._get_icon(theme)

    def render(self) -> None:
        self.parent.surface.blit(self._icon, self._get_pos())

    def render_hover(self, theme: AppTheme) -> None:
        hover: Surface = Surface(self._icon.get_size())
        hover.fill(theme.foreground)
        hover.set_alpha(HOVER_ALPHA)
        self.parent.surface.blit(hover, self._get_pos())

    def _get_icon(self, theme: AppTheme) -> Surface:
        return AssetManager.get_icon(UNDO_ICON, theme.foreground, theme.background,
                                     Vector2(min(self.parent.surface.get_size())))

    def _get_pos(self) -> Vector2:
        return Vector2(self._icon.get_rect(center=self.parent.surface.get_rect().center).topleft)

    def is_collided(self, offset: Vector2) -> bool:
        pos: Vector2 = self._get_pos() + Vector2(self.parent.placement.topleft)
        mouse_pos: Vector2 = Vector2(mouse.get_pos())
        return self._icon.get_rect().collidepoint(mouse_pos - pos - offset)
