from queue import Queue
from random import choice
from typing import NamedTuple
from typing import Optional
from typing import override

from pygame import BUTTON_LEFT
from pygame import MOUSEBUTTONDOWN
from pygame import display
from pygame.event import Event
from pygame.font import Font
from pygame.font import SysFont
from pygame.font import get_fonts
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from config.app_config import TITLE
from config.app_config import TITLE_FONT_SIZE
from events import AppEvent
from events import LaunchGameEvent
from page import Page
from puzzle_store import PuzzleDifficulty
from puzzle_store import PuzzleStore
from region import PartitionDirection
from region import Region
from themes import DifficultyThemes
from themes import GameTheme


class DifficultyCard(NamedTuple):
    region: Region
    theme: GameTheme
    difficulty: PuzzleDifficulty


class DifficultyComponent:

    def __init__(self, parent: Surface, placement: Rect) -> None:
        self._parent: Surface = parent
        self._placement: Rect = placement
        self._cards: list[DifficultyCard] = self._create_cards()

    def _create_cards(self) -> list[DifficultyCard]:
        font: Font = SysFont(get_fonts()[0], TITLE_FONT_SIZE // 2)
        cards: list[DifficultyCard] = []
        for diff_index, region in enumerate(Region.partition(self._parent, PartitionDirection.VERTICAL,
                                                             1, 1, 1, 1, 1)):
            diff: PuzzleDifficulty = PuzzleDifficulty(diff_index + 1)
            theme: GameTheme = DifficultyThemes.themes[diff]

            region.surface.fill(theme.background_primary)
            diff_name: Surface = font.render(diff.name, True, theme.foreground_primary)
            region.surface.blit(diff_name, diff_name.get_rect(center=region.surface.get_rect().center))

            region.set_hover_color(theme.foreground_primary)
            cards.append(DifficultyCard(region, theme, diff))

        return cards

    def render(self) -> None:
        collided: Optional[DifficultyCard] = self.get_collided()
        for card in self._cards:
            card.region.render()
            if collided == card:
                card.region.render_hover()

    def get_collided(self) -> Optional[DifficultyCard]:
        for card in self._cards:
            if card.region.is_collided(Vector2(self._placement.topleft)):
                return card

        return None


class MainMenu(Page):

    def __init__(self, page_id: int, events: Queue[AppEvent]) -> None:
        super().__init__(page_id, events)
        self._title_area, self._menu_area = Region.partition(display.get_surface(), PartitionDirection.VERTICAL,
                                                             1, 4)
        self._title_area.surface.fill(self.clear_color)
        self._menu_area.surface.fill(self.clear_color)

        self._diff_component: DifficultyComponent = DifficultyComponent(self._menu_area.surface,
                                                                        self._menu_area.placement)

        self._draw_title()

    def _draw_title(self) -> None:
        font: Font = SysFont(get_fonts()[0], TITLE_FONT_SIZE)
        title: Surface = font.render(TITLE, True, (0, 0, 0))
        self._title_area.surface.blit(title, title.get_rect(center=self._title_area.surface.get_rect().center))

    @override
    def parse_event(self, game_event: Event) -> None:
        if game_event.type == MOUSEBUTTONDOWN:
            if game_event.button == BUTTON_LEFT:
                if (diff := self._diff_component.get_collided()) is None:
                    return

                self.events.put(LaunchGameEvent(diff.difficulty,
                                                choice(PuzzleStore.get_puzzles(diff.difficulty)),
                                                diff.theme))

    @override
    def render(self) -> None:
        self._diff_component.render()
        self._title_area.render()
        self._menu_area.render()

    @override
    def update(self, delta_time: float) -> None:
        pass
