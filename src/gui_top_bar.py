from queue import Queue
from typing import override

from pygame.event import Event
from pygame.math import Vector2
from pygame.surface import Surface

from asset import AssetManager
from config.app_config import BACK_ICON
from config.game_config import TOP_BAR_PAD
from events import AppEvent
from gui_component import GuiComponent
from region import Region
from themes import AppTheme


class TopBar(GuiComponent):
    @override
    def render(self) -> None:
        self._back_button.render()
        if self._back_button.is_collided(Vector2(self.parent.placement.topleft)):
            self._back_button.render_hover()

        self.parent.render()

    @override
    def update(self, delta_time: float) -> None:
        pass

    @override
    def update_theme(self) -> None:
        self._back_button = self._create_back_button()
        self._back_button.set_hover_color(self._theme.foreground)
        self.parent.surface.fill(self._theme.background)

    @override
    def parse_event(self, game_event: Event, events: Queue[AppEvent]) -> None:
        pass

    def __init__(self, parent: Region, theme: AppTheme) -> None:
        super().__init__(parent, theme)
        self._back_button: Region = self._create_back_button()

    def _create_back_button(self) -> Region:
        back_surface: Surface = \
            AssetManager.get_icon(BACK_ICON, self._theme.foreground, self._theme.background,
                                  Vector2(min(self.parent.surface.get_size())) - Vector2(TOP_BAR_PAD * 2))

        return Region(self.parent.surface, back_surface, back_surface.get_rect(topleft=(TOP_BAR_PAD, TOP_BAR_PAD)))

    def is_back_collided(self) -> bool:
        return self._back_button.is_collided(Vector2(self.parent.placement.topleft))
