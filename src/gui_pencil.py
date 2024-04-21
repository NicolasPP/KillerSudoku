from typing import NamedTuple

from pygame import mouse
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from asset import AssetManager
from config.app_config import HOVER_ALPHA
from config.app_config import PENCIL_ICON
from config.app_config import SWITCH_ICON
from region import PartitionDirection
from region import Region
from themes import AppTheme


class PencilIcons(NamedTuple):
    pencil: Surface
    on: Surface
    off: Surface


class Pencil:

    def __init__(self, parent: Region, theme: AppTheme) -> None:
        self.parent: Region = parent
        self.is_on: bool = False
        self._icons: PencilIcons = self._get_icons(theme)

    def _get_icons(self, theme: AppTheme) -> PencilIcons:
        pencil_size: Vector2 = Vector2(min(self.parent.surface.get_size()))
        pencil: Surface = AssetManager.get_icon(PENCIL_ICON, theme.foreground_primary, theme.background_primary,
                                                pencil_size)
        switch: Surface = AssetManager.get_icon(SWITCH_ICON, theme.foreground_primary, theme.background_primary,
                                                pencil_size)

        on, off = Region.partition(switch, PartitionDirection.VERTICAL, 1, 1)
        on.surface.blit(switch, on.placement)
        off.surface.blit(switch, Vector2(off.placement.topleft) * -1)
        return PencilIcons(pencil, on.surface, off.surface)

    def _get_pencil_pos(self) -> Rect:
        return self._icons.pencil.get_rect(center=self.parent.surface.get_rect().center)

    def toggle(self) -> None:
        self.is_on = not self.is_on

    def redraw(self, theme: AppTheme) -> None:
        self.parent.surface.fill(theme.background_primary)
        self._icons = self._get_icons(theme)

    def render_hover(self, theme: AppTheme) -> None:
        hover_pencil: Surface = Surface(self._icons.pencil.get_size())
        status_size: Vector2 = Vector2(self._get_status().get_size())
        status_size.x //= 2
        hover_status: Surface = Surface(status_size)
        for hover in (hover_pencil, hover_status):
            hover.fill(theme.foreground_primary)
            hover.set_alpha(HOVER_ALPHA)

        pencil_pos: Rect = self._get_pencil_pos()
        self.parent.surface.blit(hover_pencil, pencil_pos)
        self.parent.surface.blit(hover_status, hover_status.get_rect(bottomleft=pencil_pos.bottomright))

    def _get_status(self) -> Surface:
        return self._icons.on if self.is_on else self._icons.off

    def render(self) -> None:
        pencil_pos: Rect = self._get_pencil_pos()
        status: Surface = self._get_status()
        self.parent.surface.blit(self._icons.pencil, pencil_pos)
        self.parent.surface.blit(status, status.get_rect(bottomleft=pencil_pos.midbottom))

    def is_collided(self, offset: Vector2) -> bool:
        # TODO: check collision with on/off surface
        pos: Vector2 = Vector2(self._get_pencil_pos().topleft) + Vector2(self.parent.placement.topleft)
        mouse_pos: Vector2 = Vector2(mouse.get_pos())
        return self._icons.pencil.get_rect().collidepoint(mouse_pos - pos - offset)
