from dataclasses import dataclass
from queue import Queue
from random import choice
from typing import NamedTuple
from typing import Optional
from typing import override

from pygame import BUTTON_LEFT
from pygame import MOUSEBUTTONUP
from pygame import display
from pygame import mouse
from pygame.event import Event
from pygame.font import Font
from pygame.font import SysFont
from pygame.font import get_fonts
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from config.app_config import HOVER_ALPHA
from config.app_config import TITLE
from config.app_config import TITLE_FONT_SIZE
from events import AppEvent
from events import LaunchGameEvent
from events import ChangeThemeEvent
from page import Page
from puzzle_store import PuzzleDifficulty
from puzzle_store import PuzzleStore
from region import PartitionDirection
from region import Region
from themes import AppTheme
from themes import Themes


class DifficultyCard(NamedTuple):
    region: Region
    difficulty: PuzzleDifficulty


class DifficultyComponent:

    def __init__(self, parent: Region, theme: AppTheme) -> None:
        self._parent: Region = parent
        self._cards: list[DifficultyCard] = self._create_cards(theme)
        self._parent.surface.fill(theme.background_primary)

    def _create_cards(self, theme: AppTheme) -> list[DifficultyCard]:
        font: Font = SysFont(get_fonts()[0], TITLE_FONT_SIZE // 2)
        cards: list[DifficultyCard] = []
        for diff_index, region in enumerate(Region.partition(self._parent.surface, PartitionDirection.VERTICAL,
                                                             1, 1, 1, 1, 1)):
            diff: PuzzleDifficulty = PuzzleDifficulty(diff_index + 1)

            region.surface.fill(theme.background_primary)
            diff_name: Surface = font.render(diff.name, True, theme.foreground_primary)
            region.surface.blit(diff_name, diff_name.get_rect(center=region.surface.get_rect().center))

            region.set_hover_color(theme.foreground_primary)
            cards.append(DifficultyCard(region, diff))

        return cards

    def render(self) -> None:
        collided: Optional[DifficultyCard] = self.get_collided()
        for card in self._cards:
            card.region.render()
            if collided == card:
                card.region.render_hover()

        self._parent.render()

    def redraw(self, theme: AppTheme) -> None:
        self._cards = self._create_cards(theme)

    def get_collided(self) -> Optional[DifficultyCard]:
        for card in self._cards:
            if card.region.is_collided(Vector2(self._parent.placement.topleft)):
                return card

        return None


@dataclass
class ThemeCard:
    region: Region
    surface: Surface
    hover: Surface
    theme: AppTheme

    def get_surface_pos(self) -> Rect:
        return self.surface.get_rect(center=self.region.surface.get_rect().center)


class ThemeComponent:

    def __init__(self, parent: Region, theme: AppTheme) -> None:
        self._parent: Region = parent
        self._theme_cards: list[ThemeCard] = self._create_theme_cards(theme)

    def _create_theme_cards(self, curr_theme: AppTheme) -> list[ThemeCard]:
        cards: list[ThemeCard] = []
        weights: list[int] = [1] * len(Themes.themes)
        for region, theme in zip(Region.partition(self._parent.surface, PartitionDirection.HORIZONTAL, *weights),
                                 Themes.themes.values()):
            surf_size: Vector2 = Vector2(min(*region.surface.get_size())) // 5

            surface: Surface = Surface(surf_size)
            surface.fill(theme.foreground_primary)
            inner: Surface = Surface(surf_size // 1.5)
            inner.fill(theme.background_primary)
            surface.blit(inner, inner.get_rect(center=surface.get_rect().center))

            hover: Surface = Surface(surf_size)
            hover.set_alpha(HOVER_ALPHA)
            hover.fill(theme.foreground_primary)

            card: ThemeCard = ThemeCard(region, surface, hover, theme)

            region.surface.fill(curr_theme.background_primary)
            region.surface.blit(surface, card.get_surface_pos())

            cards.append(card)

        return cards

    def redraw(self, theme: AppTheme) -> None:
        self._theme_cards = self._create_theme_cards(theme)

    def render(self) -> None:
        for card in self._theme_cards:
            card.region.render()

        if (collided := self.get_collided()) is not None:
            pos: Vector2 = Vector2(collided.get_surface_pos().topleft) + Vector2(collided.region.placement.topleft)
            self._parent.surface.blit(collided.hover, pos)

        self._parent.render()

    def get_collided(self) -> Optional[ThemeCard]:
        mouse_pos: Vector2 = Vector2(mouse.get_pos())
        for card in self._theme_cards:
            pos: Vector2 = Vector2(self._parent.placement.topleft) + Vector2(card.get_surface_pos().topleft) +\
                            Vector2(card.region.placement.topleft)
            if card.surface.get_rect().collidepoint(mouse_pos - pos):
                return card
        return None


class TitleComponent:

    def __init__(self, parent: Region, theme: AppTheme) -> None:
        self._parent: Region = parent
        self._draw_title(theme)

    def _draw_title(self, theme: AppTheme) -> None:
        font: Font = SysFont(get_fonts()[0], TITLE_FONT_SIZE)
        title: Surface = font.render(TITLE, True, theme.foreground_primary, theme.background_primary)
        self._parent.surface.fill(theme.background_primary)
        self._parent.surface.blit(title, title.get_rect(center=self._parent.surface.get_rect().center))

    def redraw(self, theme: AppTheme) -> None:
        self._draw_title(theme)

    def render(self) -> None:
        self._parent.render()


class MainMenu(Page):

    @override
    def parse_event(self, game_event: Event) -> None:
        if game_event.type != MOUSEBUTTONUP:
            return

        if game_event.button != BUTTON_LEFT:
            return

        self._handle_diff_press()
        self._handle_theme_press()



    @override
    def render(self) -> None:
        self._title_component.render()
        self._diff_component.render()
        self._theme_component.render()

    @override
    def update(self, delta_time: float) -> None:
        pass

    @override
    def update_theme(self, theme: AppTheme) -> None:
        self._theme = theme
        self._diff_component.redraw(self._theme)
        self._title_component.redraw(self._theme)
        self._theme_component.redraw(self._theme)

    def __init__(self, page_id: int, events: Queue[AppEvent], theme: AppTheme) -> None:
        super().__init__(page_id, events, theme)
        title_area, diff_area, theme_area = Region.partition(display.get_surface(), PartitionDirection.VERTICAL,
                                                             1, 3, 1)

        self._title_component: TitleComponent = TitleComponent(title_area, self._theme)
        self._diff_component: DifficultyComponent = DifficultyComponent(diff_area, self._theme)
        self._theme_component: ThemeComponent = ThemeComponent(theme_area, self._theme)

    def _handle_diff_press(self) -> None:
        if (diff := self._diff_component.get_collided()) is None:
            return

        self.events.put(
            LaunchGameEvent(diff.difficulty, choice(PuzzleStore.get_puzzles(diff.difficulty)))
        )

    def _handle_theme_press(self) -> None:
        if (theme := self._theme_component.get_collided()) is None:
            return

        self.events.put(
            ChangeThemeEvent(theme.theme)
        )
