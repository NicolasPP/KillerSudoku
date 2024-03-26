from queue import Queue
from random import choice
from typing import NamedTuple
from typing import Optional
from typing import override

from pygame import BUTTON_LEFT
from pygame import MOUSEBUTTONDOWN
from pygame import display
from pygame import mouse
from pygame.event import Event
from pygame.font import Font
from pygame.font import SysFont
from pygame.font import get_fonts
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from app_config import FONT_SIZE
from app_config import TITLE
from events import AppEvent
from events import LaunchGameEvent
from pages import Page
from puzzle_store import PuzzleDifficulty
from puzzle_store import PuzzleStore
from themes import DifficultyThemes
from themes import GameTheme


class DifficultyCard(NamedTuple):
    surface: Surface
    rect: Rect
    theme: GameTheme
    difficulty: PuzzleDifficulty


class DifficultyComponent:

    def __init__(self, parent: Surface, height_offset: int) -> None:
        self._parent: Surface = parent
        self._height_offset: int = height_offset
        self._font: Font = SysFont(get_fonts()[0], FONT_SIZE // 2)

        self._cards: list[DifficultyCard] = []

        self._create_cards()

    def _create_cards(self) -> None:
        cards: list[DifficultyCard] = []
        width: int = self._parent.get_width()
        height: int = self._parent.get_height() // 5

        prev_rect: Optional[Rect] = None
        for diff_index in range(1, 6):
            diff: PuzzleDifficulty = PuzzleDifficulty(diff_index)
            surface: Surface = Surface((width, height))
            theme: GameTheme = DifficultyThemes.themes[diff]
            rect: Rect = surface.get_rect()

            surface.fill(theme.background_primary)
            diff_name: Surface = self._font.render(diff.name, True, theme.foreground_primary)
            surface.blit(diff_name, diff_name.get_rect(center=rect.center))

            if prev_rect is not None:
                rect = surface.get_rect(topleft=prev_rect.bottomleft)

            cards.append(DifficultyCard(surface, rect, theme, diff))

            prev_rect = rect

        self._cards = cards

    def render(self) -> None:
        collided: Optional[DifficultyCard] = self.get_collided()
        for card in self._cards:
            self._parent.blit(card.surface, card.rect)
            if collided == card:
                hover: Surface = Surface(card.surface.get_size())
                hover.set_alpha(100)
                hover.fill(card.theme.foreground_primary)
                self._parent.blit(hover, card.rect)

    def get_collided(self) -> Optional[DifficultyCard]:
        mouse_pos: Vector2 = Vector2(mouse.get_pos())
        mouse_pos.y -= self._height_offset

        for card in self._cards:
            if card.rect.collidepoint(*mouse_pos.xy):
                return card

        return None


class MainMenu(Page):

    def __init__(self, page_id: int, events: Queue[AppEvent]) -> None:
        super().__init__(page_id, events)
        self._font: Font = SysFont(get_fonts()[0], FONT_SIZE)

        app_width: int = display.get_surface().get_width()
        app_height: int = display.get_surface().get_height()
        height_fifth: int = app_height // 5

        self._title_area: Surface = Surface((app_width, height_fifth))
        self._title_area.fill(self.get_bg_color())

        self._menu_area: Surface = Surface((app_width, height_fifth * 4))
        self._menu_area.fill(self.get_bg_color())

        self._diff_component: DifficultyComponent = DifficultyComponent(self._menu_area, height_fifth)

        self._draw_title()

    def _draw_title(self) -> None:
        title: Surface = self._font.render(TITLE, True, (0, 0, 0))
        self._title_area.blit(title, title.get_rect(center=self._title_area.get_rect().center))

    @override
    def parse_event(self, event: Event) -> None:
        if event.type == MOUSEBUTTONDOWN:
            if event.button == BUTTON_LEFT:
                collided: Optional[DifficultyCard] = self._diff_component.get_collided()
                if collided is None:
                    return

                self.events.put(LaunchGameEvent(collided.difficulty,
                                                choice(PuzzleStore.get_puzzles(collided.difficulty)),
                                                collided.theme))

    @override
    def render(self) -> None:
        self._diff_component.render()
        display.get_surface().blit(self._title_area, (0, 0))
        display.get_surface().blit(self._menu_area, (0, self._title_area.get_height()))

    @override
    def update(self, delta_time: float) -> None:
        pass
