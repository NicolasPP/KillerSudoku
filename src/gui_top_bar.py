from queue import Queue
from typing import override

from pygame.event import Event
from pygame.font import Font
from pygame.font import SysFont
from pygame.font import get_fonts
from pygame.math import Vector2
from pygame.surface import Surface

from asset import AssetManager
from config.app_config import BACK_ICON
from config.game_config import TOP_BAR_PAD
from events import AppEvent
from gui_component import GuiComponent
from region import Region
from themes import AppTheme


class Timer:

    def __init__(self) -> None:
        self._time_passed: float = 0
        self.enabled: bool = False

    def pass_time(self, time: float) -> None:
        self._time_passed += time

    def reset(self) -> None:
        self._time_passed = 0.0

    def __str__(self) -> str:
        hours: int = int(self._time_passed // 3600)
        remaining_seconds: float = self._time_passed % 3600
        minutes: int = int(remaining_seconds // 60)
        remaining_seconds: int = int(remaining_seconds % 60)
        return f"{hours:02} - {minutes:02} - {remaining_seconds:02}"


class TopBar(GuiComponent):
    @override
    def render(self) -> None:
        self._back_button.render()
        if self._back_button.is_collided(Vector2(self.parent.placement.topleft)):
            self._back_button.render_hover()

        self._killer_calc.render()
        self._clock.render()

        self.parent.render()

    @override
    def update(self, delta_time: float) -> None:
        if self._timer.enabled:
            self._timer.pass_time(delta_time)
            self._clock = self._create_clock()

    @override
    def update_theme(self) -> None:
        self._back_button = self._create_back_button()
        self._killer_calc = self._create_killer_calc()
        self._clock = self._create_clock()
        self._back_button.set_hover_color(self._theme.foreground)
        self._killer_calc.set_hover_color(self._theme.foreground)
        self._clock.set_hover_color(self._theme.foreground)
        self.parent.surface.fill(self._theme.background)

    @override
    def parse_event(self, game_event: Event, events: Queue[AppEvent]) -> None:
        pass

    def __init__(self, parent: Region, theme: AppTheme) -> None:
        super().__init__(parent, theme)
        self._timer: Timer = Timer()
        self._font: Font = SysFont(get_fonts()[0], 50)
        self._back_button: Region = self._create_back_button()
        self._clock: Region = self._create_clock()
        self._killer_calc: Region = self._create_killer_calc()

    def set_selection_sum(self, selection_sum: int) -> None:
        sum_render: Surface = self._font.render(str(selection_sum), True, self.theme.foreground, self.theme.background)
        self._killer_calc.surface.fill(self.theme.background)
        self._killer_calc.surface.blit(sum_render,
                                       sum_render.get_rect(center=self._killer_calc.surface.get_rect().center))

    def begin_timer(self) -> None:
        self._timer.enabled = True

    def reset_timer(self) -> None:
        self._timer.reset()

    def _create_clock(self) -> Region:
        clock_surface: Surface = SysFont(get_fonts()[0], 40).render(str(self._timer), True, self._theme.foreground,
                                                                    self._theme.background)
        mid_bottom: Vector2 = Vector2(self.parent.surface.get_rect().midbottom)
        mid_bottom.y -= TOP_BAR_PAD * 2
        return Region(self.parent.surface, clock_surface, clock_surface.get_rect(midbottom=mid_bottom))

    def _create_killer_calc(self) -> Region:
        calc_surf: Surface = Surface(self._font.size("0000"))
        calc_surf.fill(self.theme.background)
        return Region(self.parent.surface, calc_surf,
                      calc_surf.get_rect(topright=(self.parent.surface.get_width() - TOP_BAR_PAD, TOP_BAR_PAD)))

    def _create_back_button(self) -> Region:
        back_surface: Surface = \
            AssetManager.get_icon(BACK_ICON, self._theme.foreground, self._theme.background,
                                  Vector2(min(self.parent.surface.get_size())) - Vector2(TOP_BAR_PAD * 2))

        return Region(self.parent.surface, back_surface, back_surface.get_rect(topleft=(TOP_BAR_PAD, TOP_BAR_PAD)))

    def is_back_collided(self) -> bool:
        return self._back_button.is_collided(Vector2(self.parent.placement.topleft))
