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
from events import AppEvent
from events import SetPageEvent
from gui_component import GuiComponent
from region import Region
from themes import GameTheme


class TopBar(GuiComponent):

    def __init__(self, parent: Region, theme: GameTheme) -> None:
        super().__init__(parent, theme)
        back_surface: Surface = AssetManager.get_icon(BACK_ICON, theme.background_primary)
        self._back_button: Region = Region(
            parent.surface, back_surface,
            back_surface.get_rect(topleft=(0, 0))
        )

    @override
    def update_theme(self) -> None:
        self._back_button.set_hover_color(self._theme.foreground_primary)
        self._parent.surface.fill(self._theme.background_primary)

    @override
    def render(self) -> None:
        self._back_button.render()
        if self._back_button.is_collided(Vector2(self._parent.placement.topleft)):
            self._back_button.render_hover()

        self._parent.render()

    @override
    def parse_event(self, game_event: Event, events: Queue[AppEvent]) -> None:
        if game_event.type == MOUSEBUTTONDOWN:
            if game_event.button == BUTTON_LEFT:
                if self._back_button.is_collided(Vector2(self._parent.placement.topleft)):
                    events.put(SetPageEvent(MAIN_MENU_PAGE))

    @override
    def update(self, delta_time: float) -> None:
        pass
