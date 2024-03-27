from itertools import chain
from queue import Queue
from typing import Optional
from typing import override

from pygame import display
from pygame.event import Event
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from events import AppEvent
from pages import Page
from puzzle_store import Puzzle
from puzzle_store import PuzzleDifficulty
from region import Region
from themes import GameTheme
from app_config import HOVER_ALPHA
from app_config import BOARD_SIZE

type Board = list[list[int]]


class KillerSudokuState:

    def __init__(self) -> None:
        self._puzzle: Optional[Puzzle] = None
        self._board: Board = [[0] * 9 for _ in range(9)]

    def set_puzzle(self, puzzle: Puzzle) -> None:
        self._puzzle = puzzle

    def get_puzzle(self) -> Puzzle:
        assert self._puzzle is not None, "Puzzle has not been set"
        return self._puzzle


class BoardDisplay:

    def __init__(self, parent: Surface, parent_placement: Rect, state: KillerSudokuState) -> None:
        self._state: KillerSudokuState = state
        self._parent: Surface = parent
        self._parent_placement: Rect = parent_placement
        self._cells: list[list[Region]] = []
        self._surface: Surface = self._create_board_surface()
        self._theme: Optional[GameTheme] = None

    def _create_board_surface(self) -> Surface:
        cells: list[list[Region]] = []
        cell_size: int = (min(self._parent.get_width(), self._parent.get_height()) // 9) - 2
        board: Surface = Surface(Vector2((cell_size * BOARD_SIZE) + 12))
        row_padding: int = 1
        for row in range(BOARD_SIZE):
            region_row: list[Region] = []
            col_padding: int = 1
            for col in range(BOARD_SIZE):
                placement: Rect = Rect((col * (cell_size + 1)) + col_padding, (row * (cell_size + 1)) + row_padding,
                                       cell_size, cell_size)
                surface: Surface = Surface(placement.size)

                if (col + 1) % 3 == 0:
                    col_padding += 1

                region_row.append(Region(board, surface, placement))

            if (row + 1) % 3 == 0:
                row_padding += 1

            cells.append(region_row)

        self._cells = cells
        return board

    def update_colors(self, theme: GameTheme) -> None:
        self._theme = theme
        self._surface.fill(theme.foreground_primary)
        for cell in chain.from_iterable(self._cells):
            cell.surface.fill(theme.background_primary)

    def render(self) -> None:
        for cell in chain.from_iterable(self._cells):
            cell.render()
            if cell.is_collided(self._get_collision_offset()):
                hover: Surface = Surface(Vector2(cell.surface.get_size()) - Vector2(2))
                hover.set_alpha(HOVER_ALPHA)
                hover.fill(self._theme.foreground_primary)
                self._surface.blit(hover, Vector2(cell.placement.topleft) + Vector2(1))

        self._parent.blit(self._surface, self._surface.get_rect(center=self._parent.get_rect().center))

    def _get_collision_offset(self) -> Vector2:
        return Vector2(self._parent_placement.topleft) + \
            Vector2(self._surface.get_rect(center=self._parent.get_rect().center).topleft)


class KillerSudoku(Page):
    @override
    def __init__(self, page_id: int, events: Queue[AppEvent]) -> None:
        super().__init__(page_id, events)
        self._state: KillerSudokuState = KillerSudokuState()
        self.difficulty: Optional[PuzzleDifficulty] = None
        self.theme: Optional[GameTheme] = None

        self.top_bar, self.body, self.tools = Region.stack(display.get_surface(), 3, 19, 3)
        self.board_display: BoardDisplay = BoardDisplay(self.body.surface, self.body.placement, self._state)

    def set_puzzle_info(self, difficulty: PuzzleDifficulty, puzzle: Puzzle, theme: GameTheme) -> None:
        self._state.set_puzzle(puzzle)
        self.difficulty = difficulty
        self.theme = theme

        self.top_bar.surface.fill(self.theme.background_primary)
        self.body.surface.fill(self.theme.background_primary)
        self.tools.surface.fill(self.theme.background_primary)
        self.board_display.update_colors(self.theme)

    @override
    def parse_event(self, game_event: Event) -> None:
        pass

    @override
    def render(self) -> None:
        self.top_bar.render()

        self.board_display.render()
        self.body.render()

        self.tools.render()

    @override
    def update(self, delta_time: float) -> None:
        pass
