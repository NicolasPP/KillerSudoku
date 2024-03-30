from enum import Enum
from enum import auto
from itertools import chain
from queue import Queue
from typing import NamedTuple
from typing import Optional
from typing import override

from pygame import BUTTON_LEFT
from pygame import MOUSEBUTTONDOWN
from pygame import display
from pygame import draw
from pygame.event import Event
from pygame.font import Font
from pygame.font import SysFont
from pygame.font import get_fonts
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from app_config import BOARD_SIZE
from app_config import CAGE_PAD
from app_config import MAIN_MENU_PAGE
from events import AppEvent
from events import LaunchGameEvent
from events import SetPageEvent
from game_config import BACK_BUTTON
from game_config import BACK_FONT_SIZE
from game_config import SUM_FONT_SIZE
from pages import Page
from puzzle_store import Puzzle
from puzzle_store import PuzzleDifficulty
from region import Region
from themes import GameTheme

type Board = list[list[int]]


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class Neighbour(NamedTuple):
    direction: Direction
    row: int
    col: int


class KillerSudokuState:

    def __init__(self) -> None:
        self._puzzle: Optional[Puzzle] = None
        self._board: Board = [[0] * 9 for _ in range(9)]

    @property
    def puzzle(self) -> Puzzle:
        assert self._puzzle is not None, "Puzzle has not been set"
        return self._puzzle

    @puzzle.setter
    def puzzle(self, puzzle: Puzzle) -> None:
        self._puzzle = puzzle

    @puzzle.deleter
    def puzzle(self) -> None:
        del self._puzzle


class BoardDisplay:

    def __init__(self, parent: Surface, parent_placement: Rect, state: KillerSudokuState) -> None:
        self._state: KillerSudokuState = state
        self._parent: Surface = parent
        self._parent_placement: Rect = parent_placement
        self._cells: list[list[Region]] = []
        self._theme: Optional[GameTheme] = None
        self._surface: Surface = self._create_board_surface()

    def _create_board_surface(self) -> Surface:
        cells: list[list[Region]] = []
        cell_size: int = (min(self._parent.get_width(), self._parent.get_height()) // BOARD_SIZE) - 2
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

    def _get_neighbours(self, row: int, col: int) -> list[Neighbour]:
        neighbours: list[Neighbour] = []
        if row >= len(self._cells) or row < 0:
            return neighbours

        if col >= len(self._cells[0]) or col < 0:
            return neighbours

        for row_offset, col_offset, direction in \
                [(1, 0, Direction.DOWN), (-1, 0, Direction.UP), (0, 1, Direction.RIGHT), (0, -1, Direction.LEFT)]:
            n_row: int = row + row_offset
            n_col: int = col + col_offset

            if n_row >= len(self._cells) or n_row < 0:
                continue

            if n_col >= len(self._cells[0]) or n_col < 0:
                continue

            neighbours.append(Neighbour(direction, n_row, n_col))

        return neighbours

    def _draw_cages(self) -> None:
        font: Font = SysFont(get_fonts()[0], SUM_FONT_SIZE)
        for cage_sum, cells in self._state.puzzle.cages:
            present_cells: set[tuple[int, int]] = set(cells)
            sum_row, sum_col = cells[-1]
            sum_cell: Region = self._cells[sum_row][sum_col]
            sum_surface: Surface = font.render(str(cage_sum), True, self._theme.foreground_primary,
                                               self._theme.background_primary)
            for row, col in cells:
                neighbours: list[Neighbour] = self._get_neighbours(row, col)
                present_neighbours: list[Neighbour] = list(
                    filter(lambda n: (n.row, n.col) in present_cells, neighbours))

                draw_cage_side(self._cells[row][col], set([n.direction for n in present_neighbours]), self._theme)

            sum_cell.surface.blit(sum_surface, (0, 0))

    def update_colors(self, theme: GameTheme) -> None:
        self._theme = theme
        self._surface.fill(theme.foreground_primary)
        for cell in chain.from_iterable(self._cells):
            cell.surface.fill(theme.background_primary)
            cell.set_hover_color(theme.foreground_primary)

        self._draw_cages()

    def render(self) -> None:
        for cell in chain.from_iterable(self._cells):
            cell.render()
            if cell.is_collided(self._get_collision_offset()):
                cell.render_hover()

        self._parent.blit(self._surface, self._surface.get_rect(center=self._parent.get_rect().center))

    def _get_collision_offset(self) -> Vector2:
        return Vector2(self._parent_placement.topleft) + \
            Vector2(self._surface.get_rect(center=self._parent.get_rect().center).topleft)


class KillerSudoku(Page):
    @override
    def __init__(self, page_id: int, events: Queue[AppEvent]) -> None:
        super().__init__(page_id, events)
        self._state: KillerSudokuState = KillerSudokuState()
        self._difficulty: Optional[PuzzleDifficulty] = None
        self._theme: GameTheme = GameTheme.default()

        self._top_bar, self._body, self._tools = Region.stack(display.get_surface(), 2, 19, 4)
        self._board_display: BoardDisplay = BoardDisplay(self._body.surface, self._body.placement, self._state)

        font: Font = SysFont(get_fonts()[0], BACK_FONT_SIZE)

        back_surface: Surface = font.render(BACK_BUTTON, True, self._theme.foreground_primary,
                                            self._theme.background_primary)
        self._back_button: Region = Region(
            self._tools.surface, back_surface,
            back_surface.get_rect(bottomleft=self._tools.surface.get_rect().bottomleft)
        )

    def process_launch_game_event(self, launch_game: LaunchGameEvent) -> None:
        self._state.puzzle = launch_game.puzzle
        self._difficulty = launch_game.difficulty
        self._theme = launch_game.theme

        self._back_button.set_hover_color(self._theme.foreground_primary)
        self._top_bar.surface.fill(self._theme.background_primary)
        self._body.surface.fill(self._theme.background_primary)
        self._tools.surface.fill(self._theme.background_primary)
        self._board_display.update_colors(self._theme)

    @override
    def parse_event(self, game_event: Event) -> None:
        if game_event.type == MOUSEBUTTONDOWN:
            if game_event.button == BUTTON_LEFT:
                if self._back_button.is_collided(Vector2(self._tools.placement.topleft)):
                    self.events.put(SetPageEvent(MAIN_MENU_PAGE))

    @override
    def render(self) -> None:
        self._top_bar.render()

        self._board_display.render()
        self._body.render()

        self._back_button.render()
        if self._back_button.is_collided(Vector2(self._tools.placement.topleft)):
            self._back_button.render_hover()

        self._tools.render()

    @override
    def update(self, delta_time: float) -> None:
        pass


def draw_cage_side(cell: Region, excluded_directions: set[Direction], theme: GameTheme) -> None:
    for direction in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
        if direction in excluded_directions:
            continue

        if direction is Direction.UP:
            draw.line(cell.surface, theme.foreground_primary,
                      Vector2(CAGE_PAD), Vector2(cell.surface.get_width() - CAGE_PAD, CAGE_PAD))

        elif direction is Direction.DOWN:
            draw.line(cell.surface, theme.foreground_primary,
                      Vector2(CAGE_PAD, cell.surface.get_height() - CAGE_PAD),
                      Vector2(cell.surface.get_height() - CAGE_PAD, cell.surface.get_width() - CAGE_PAD))

        elif direction is Direction.LEFT:
            draw.line(cell.surface, theme.foreground_primary,
                      Vector2(CAGE_PAD), Vector2(CAGE_PAD, cell.surface.get_width() - CAGE_PAD))

        elif direction is Direction.RIGHT:
            draw.line(cell.surface, theme.foreground_primary,
                      Vector2(cell.surface.get_height() - CAGE_PAD, CAGE_PAD),
                      Vector2(cell.surface.get_height() - CAGE_PAD, cell.surface.get_width() - CAGE_PAD))

        else:
            raise Exception(f"Direction: {direction.name} not recognised")
