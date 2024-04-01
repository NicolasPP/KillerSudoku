from enum import Enum
from enum import auto
from itertools import chain
from queue import Queue
from typing import NamedTuple
from typing import override

from pygame import draw
from pygame.event import Event
from pygame.font import Font
from pygame.font import SysFont
from pygame.font import get_fonts
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from config.app_config import BOARD_SIZE
from config.app_config import CAGE_PAD
from config.game_config import SUM_FONT_SIZE
from events import AppEvent
from gui_component import GuiComponent
from killer_sudoku_state import KillerSudokuState
from region import Region
from themes import GameTheme


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class Neighbour(NamedTuple):
    direction: Direction
    row: int
    col: int


class BoardGui(GuiComponent):

    def __init__(self, parent: Region, theme: GameTheme, state: KillerSudokuState) -> None:
        super().__init__(parent, theme)
        self._state: KillerSudokuState = state
        self._cells: list[list[Region]] = []
        self._surface: Surface = self._create_board_surface()

    def _create_board_surface(self) -> Surface:
        cells: list[list[Region]] = []
        cell_size: int = (min(self._parent.surface.get_width(), self._parent.surface.get_height()) // BOARD_SIZE) - 2
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

                self._draw_cage_side(row, col, set([n.direction for n in present_neighbours]))

            sum_cell.surface.blit(sum_surface, (0, 0))

    def _draw_cage_side(self, row: int, col: int, excluded_directions: set[Direction]) -> None:
        cell: Region = self._cells[row][col]
        for direction in {Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT} - excluded_directions:
            if direction is Direction.UP:
                draw.line(cell.surface, self._theme.foreground_primary,
                          Vector2(CAGE_PAD), Vector2(cell.surface.get_width() - CAGE_PAD, CAGE_PAD))

            elif direction is Direction.DOWN:
                draw.line(cell.surface, self._theme.foreground_primary,
                          Vector2(CAGE_PAD, cell.surface.get_height() - CAGE_PAD),
                          Vector2(cell.surface.get_height() - CAGE_PAD, cell.surface.get_width() - CAGE_PAD))

            elif direction is Direction.LEFT:
                draw.line(cell.surface, self._theme.foreground_primary,
                          Vector2(CAGE_PAD), Vector2(CAGE_PAD, cell.surface.get_width() - CAGE_PAD))

            elif direction is Direction.RIGHT:
                draw.line(cell.surface, self._theme.foreground_primary,
                          Vector2(cell.surface.get_height() - CAGE_PAD, CAGE_PAD),
                          Vector2(cell.surface.get_height() - CAGE_PAD, cell.surface.get_width() - CAGE_PAD))

            else:
                raise Exception(f"Direction: {direction.name} not recognised")

    def _get_collision_offset(self) -> Vector2:
        return Vector2(self._parent.placement.topleft) + \
            Vector2(self._surface.get_rect(center=self._parent.surface.get_rect().center).topleft)

    @override
    def update_theme(self) -> None:
        self._parent.surface.fill(self._theme.background_primary)
        self._surface.fill(self._theme.foreground_primary)
        for cell in chain.from_iterable(self._cells):
            cell.surface.fill(self._theme.background_primary)
            cell.set_hover_color(self._theme.foreground_primary)

        self._draw_cages()

    @override
    def render(self) -> None:
        for cell in chain.from_iterable(self._cells):
            cell.render()
            if cell.is_collided(self._get_collision_offset()):
                cell.render_hover()

        self._parent.surface.blit(
            self._surface, self._surface.get_rect(center=self._parent.surface.get_rect().center))

        self._parent.render()

    @override
    def parse_event(self, game_event: Event, events: Queue[AppEvent]) -> None:
        pass

    @override
    def update(self, delta_time: float) -> None:
        pass