from __future__ import annotations

from enum import Enum
from enum import auto
from typing import Optional

from pygame import mouse
from pygame.color import Color
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from config.app_config import HOVER_ALPHA


class PartitionDirection(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()


class Region:
    @staticmethod
    def partition(parent: Surface, direction: PartitionDirection, *weights: int) -> list[Region]:
        # Vertical stack Only
        # Works best when weights divides parents height with no remainder
        if (total_weight := sum(weights)) < len(weights):
            raise Exception("weights cannot be 0 or negative")

        def get_direction_dimension() -> int:
            return parent.get_height() if direction is PartitionDirection.VERTICAL else parent.get_width()

        def get_region_dimension(unit_length: int) -> tuple[int, int]:
            if direction is PartitionDirection.VERTICAL:
                return parent.get_width(), unit_length

            return unit_length, parent.get_height()

        def get_placement_rect(region_surface: Surface) -> Rect:
            if prev_placement is None:
                return region_surface.get_rect()

            top_left_destination: tuple[int, int] = prev_placement.bottomleft
            if direction is PartitionDirection.HORIZONTAL:
                top_left_destination = prev_placement.topright

            return region_surface.get_rect(topleft=top_left_destination)

        regions: list[Region] = []
        unit: int = get_direction_dimension() // total_weight
        prev_placement: Optional[Rect] = None
        for weight in weights:
            length: int = unit * weight
            surface: Surface = Surface(get_region_dimension(length))
            placement: Rect = get_placement_rect(surface)
            regions.append(Region(parent, surface, placement))
            prev_placement = placement

        return regions

    def __init__(self, parent: Surface, surface: Surface, placement: Rect) -> None:
        self._hover: Surface = Surface(surface.get_size())
        self._parent: Surface = parent
        self._surface: Surface = surface
        self._placement: Rect = placement

    @property
    def surface(self) -> Surface:
        return self._surface

    @surface.setter
    def surface(self, surf: Surface) -> None:
        self._surface = surf

    @surface.deleter
    def surface(self) -> None:
        del self._surface

    @property
    def placement(self) -> Rect:
        return self._placement

    @placement.setter
    def placement(self, place: Rect) -> None:
        self._placement = place

    @placement.deleter
    def placement(self) -> None:
        del self._placement

    def render(self) -> None:
        self._parent.blit(self._surface, self._placement)

    def is_collided(self, parent_placement: Vector2) -> bool:
        mouse_pos: Vector2 = Vector2(mouse.get_pos()) - parent_placement
        return self._placement.collidepoint(*mouse_pos.xy)

    def set_hover_color(self, color: Color) -> None:
        self._hover.fill(color)
        self._hover.set_alpha(HOVER_ALPHA)

    def render_hover(self) -> None:
        self._parent.blit(self._hover, self._placement)
