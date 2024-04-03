from queue import Queue
from typing import override

from pygame import BUTTON_LEFT
from pygame import MOUSEBUTTONDOWN
from pygame.event import Event
from pygame.math import Vector2
from pygame.surface import Surface

from asset import AssetManager
from config.app_config import BACK_ICON
from config.app_config import MAIN_MENU_PAGE
from config.game_config import TOP_BAR_PAD
from events import AppEvent
from events import SetPageEvent
from gui_component import GuiComponent
from region import Region
from themes import GameTheme


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
        self._back_button.set_hover_color(self._theme.foreground_primary)
        self.parent.surface.fill(self._theme.background_primary)

    @override
    def parse_event(self, game_event: Event, events: Queue[AppEvent]) -> None:
        if game_event.type == MOUSEBUTTONDOWN:
            if game_event.button == BUTTON_LEFT:
                if self._back_button.is_collided(Vector2(self.parent.placement.topleft)):
                    events.put(SetPageEvent(MAIN_MENU_PAGE))

    def __init__(self, parent: Region, theme: GameTheme) -> None:
        super().__init__(parent, theme)
        back_surface: Surface = \
            AssetManager.get_icon(BACK_ICON, theme.background_primary,
                                  Vector2(min(self.parent.surface.get_size())) - Vector2(TOP_BAR_PAD * 2))

        self._back_button: Region = Region(
            parent.surface, back_surface,
            back_surface.get_rect(topleft=(TOP_BAR_PAD, TOP_BAR_PAD))
        )
