from pygame.math import Vector2

from gui_eraser import Eraser
from region import PartitionDirection
from region import Region
from themes import GameTheme


class Tools:
    def __init__(self, parent: Region, theme: GameTheme) -> None:
        self.parent: Region = parent
        undo_region, pencil_region, erase_region = \
            Region.partition(self.parent.surface, PartitionDirection.HORIZONTAL, 1, 1, 1)

        self.eraser: Eraser = Eraser(erase_region, theme)

    def render(self, offset: Vector2, theme: GameTheme) -> None:
        self.eraser.render()

        if self.is_eraser_collided(offset):
            self.eraser.hover(theme)

        self.eraser.parent.render()
        self.parent.render()

    def redraw(self, theme: GameTheme) -> None:
        self.parent.surface.fill(theme.foreground_primary)
        self.eraser.redraw(theme)

    def is_eraser_collided(self, offset: Vector2) -> bool:
        return self.eraser.is_collided(offset)
