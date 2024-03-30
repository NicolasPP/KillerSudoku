from __future__ import annotations

from typing import Optional

from pygame import mouse
from pygame.color import Color
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from app_config import HOVER_ALPHA


class Region:
    @staticmethod
    def stack(parent: Surface, *weights: int) -> list[Region]:
        # Vertical stack Only
        # Works best when weights divides parents height with no remainder

        regions: list[Region] = []

        if (total_weight := sum(weights)) < len(weights):
            raise Exception("weights cannot be 0 or negative")

        unit: int = parent.get_height() // total_weight
        prev_placement: Optional[Rect] = None
        for weight in weights:
            height: int = unit * weight
            surface: Surface = Surface((parent.get_width(), height))
            placement: Rect = surface.get_rect()

            if prev_placement is not None:
                placement = surface.get_rect(topleft=prev_placement.bottomleft)

            regions.append(Region(parent, surface, placement))
            prev_placement = placement

        return regions

    def __init__(self, parent: Surface, surface: Surface, placement: Rect) -> None:
        self._parent: Surface = parent
        self.surface: Surface = surface
        self.placement: Rect = placement
        self._hover: Surface = Surface(self.surface.get_size())

    def render(self) -> None:
        self._parent.blit(self.surface, self.placement)

    def is_collided(self, parent_placement: Vector2) -> bool:
        mouse_pos: Vector2 = Vector2(mouse.get_pos()) - parent_placement
        return self.placement.collidepoint(*mouse_pos.xy)

    def set_hover_color(self, color: Color) -> None:
        self._hover.fill(color)
        self._hover.set_alpha(HOVER_ALPHA)

    def render_hover(self) -> None:
        self._parent.blit(self._hover, self.placement)
