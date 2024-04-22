from pygame.math import Vector2

from gui_eraser import Eraser
from gui_pencil import Pencil
from region import PartitionDirection
from region import Region
from themes import AppTheme
from gui_undo import Undo


class Tools:
    def __init__(self, parent: Region, theme: AppTheme) -> None:
        self.parent: Region = parent
        undo_region, pencil_region, erase_region = \
            Region.partition(self.parent.surface, PartitionDirection.HORIZONTAL, 1, 1, 1)

        self.pencil: Pencil = Pencil(pencil_region, theme)
        self.eraser: Eraser = Eraser(erase_region, theme)
        self.undo: Undo = Undo(undo_region, theme)

    def render(self, offset: Vector2, theme: AppTheme) -> None:
        # eraser
        self.eraser.render()
        if self.eraser.is_collided(offset):
            self.eraser.hover(theme)
        self.eraser.parent.render()

        # pencil
        self.pencil.render()
        if self.pencil.is_collided(offset):
            self.pencil.render_hover(theme)
        self.pencil.parent.render()

        # undo
        self.undo.render()
        if self.undo.is_collided(offset):
            self.undo.render_hover(theme)
        self.undo.parent.render()

        self.parent.render()

    def redraw(self, theme: AppTheme) -> None:
        self.parent.surface.fill(theme.foreground)
        self.eraser.redraw(theme)
        self.pencil.redraw(theme)
        self.undo.redraw(theme)
