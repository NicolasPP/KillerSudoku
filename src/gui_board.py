from enum import Enum
from enum import auto
from functools import cache
from itertools import chain
from queue import Queue
from typing import Optional
from typing import override

from pygame import BUTTON_LEFT
from pygame import MOUSEBUTTONDOWN
from pygame import draw
from pygame.event import Event
from pygame.font import Font
from pygame.font import SysFont
from pygame.font import get_fonts
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from config.app_config import BOARD_SIZE
from config.game_config import CAGE_PAD
from config.game_config import CELL_PAD
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

    def get(self) -> Vector2:
        direction: Direction = Direction[self.name]
        if direction is Direction.UP:
            return Vector2(-1, 0)

        elif direction is Direction.DOWN:
            return Vector2(1, 0)

        elif direction is Direction.LEFT:
            return Vector2(0, -1)

        elif direction is Direction.RIGHT:
            return Vector2(0, 1)

        else:
            raise Exception()


class Cell:

    def __init__(self, region: Region, row: int, col: int) -> None:
        self.region: Region = region
        self.row: int = row
        self.col: int = col


class BoardGui(GuiComponent):
    @override
    def render(self) -> None:
        for cell in chain.from_iterable(self._cells):
            cell.region.render()

        if self._require_redraw:
            self._draw_board_vals()
            self._draw_cages()
            self._require_redraw = False

        self._render_selected()
        self.parent.surface.blit(self._surface,
                                 self._surface.get_rect(center=self.parent.surface.get_rect().center))
        self.parent.render()

    @override
    def update(self, delta_time: float) -> None:
        pass

    @override
    def update_theme(self) -> None:
        self.parent.surface.fill(self._theme.background_primary)
        self._surface.fill(self._theme.foreground_primary)
        for cell in chain.from_iterable(self._cells):
            cell.region.surface.fill(self._theme.background_primary)
            cell.region.set_hover_color(self._theme.foreground_primary)

        self._draw_cages()

    @override
    def parse_event(self, game_event: Event, events: Queue[AppEvent]) -> None:
        if game_event.type == MOUSEBUTTONDOWN:
            if game_event.button == BUTTON_LEFT:
                self._set_selected()

    def __init__(self, parent: Region, theme: GameTheme, state: KillerSudokuState) -> None:
        super().__init__(parent, theme)
        self._state: KillerSudokuState = state
        self._cells: list[list[Cell]] = []
        self._surface: Surface = self._create_board_surface()
        self._selected: Optional[Cell] = None
        self._require_redraw: bool = True

    @property
    def selected(self) -> Optional[Cell]:
        return self._selected

    @selected.setter
    def selected(self, cell: Cell) -> None:
        self._selected = cell

    @selected.deleter
    def selected(self) -> None:
        del self._selected

    @property
    def require_redraw(self) -> bool:
        return self._require_redraw

    @require_redraw.setter
    def require_redraw(self, redraw: bool) -> None:
        self._require_redraw = redraw

    @require_redraw.deleter
    def require_redraw(self) -> None:
        del self._require_redraw

    def _create_board_surface(self) -> Surface:
        cells: list[list[Cell]] = []
        cell_size: int = (min(self.parent.surface.get_width(), self.parent.surface.get_height()) // BOARD_SIZE) - \
                         (CELL_PAD * 2)
        board: Surface = Surface(Vector2((cell_size * BOARD_SIZE) + (14 * CELL_PAD)))
        row_padding: int = CELL_PAD
        for row in range(BOARD_SIZE):
            region_row: list[Cell] = []
            col_padding: int = CELL_PAD
            for col in range(BOARD_SIZE):
                placement: Rect = Rect((col * (cell_size + CELL_PAD)) + col_padding,
                                       (row * (cell_size + CELL_PAD)) + row_padding, cell_size, cell_size)
                surface: Surface = Surface(placement.size)

                if (col + 1) % 3 == 0:
                    col_padding += CELL_PAD * 2

                region_row.append(Cell(Region(board, surface, placement), row, col))

            if (row + 1) % 3 == 0:
                row_padding += CELL_PAD * 2

            cells.append(region_row)

        self._cells = cells
        return board

    @cache
    def _get_neighbours(self, row: int, col: int) -> set[Direction]:
        neighbours: set[Direction] = set()
        if row >= len(self._cells) or row < 0:
            return neighbours

        if col >= len(self._cells[0]) or col < 0:
            return neighbours

        for direction in [Direction.DOWN, Direction.UP, Direction.RIGHT, Direction.LEFT]:
            index: Vector2 = Vector2(row, col) + direction.get()

            if index.x >= len(self._cells) or index.x < 0:
                continue

            if index.y >= len(self._cells[0]) or index.y < 0:
                continue

            neighbours.add(direction)

        return neighbours

    def _get_present_neighbours(self, row: int, col: int, present_cells: set[tuple[int, int]]) -> set[Direction]:
        neighbours: set[Direction] = self._get_neighbours(row, col)
        present: set[Direction] = set()
        for neighbour in neighbours:
            index: Vector2 = Vector2(row, col) + neighbour.get()
            if (index.x, index.y) in present_cells:
                present.add(neighbour)

        return present

    def _draw_cages(self) -> None:
        font: Font = SysFont(get_fonts()[0], SUM_FONT_SIZE)
        for cage_sum, cells in self._state.puzzle.cages:
            present_cells: set[tuple[int, int]] = set(cells)
            sum_row, sum_col = cells[-1]
            sum_cell: Cell = self._cells[sum_row][sum_col]
            sum_surface: Surface = font.render(str(cage_sum), True, self._theme.foreground_primary,
                                               self._theme.background_primary)
            for row, col in cells:
                neighbours: set[Direction] = self._get_present_neighbours(row, col, present_cells)
                self._draw_cage_side(row, col, neighbours)
                self._draw_cage_corner(row, col, neighbours, cells)

            sum_cell.region.surface.blit(sum_surface, sum_surface.get_rect(center=(CAGE_PAD, CAGE_PAD)))

    def _draw_cage_corner(self, row: int, col: int, neighbours: set[Direction], cage: list[tuple[int, int]]) -> None:
        cell_surface: Surface = self._cells[row][col].region.surface
        cell_size: Vector2 = Vector2(cell_surface.get_size())
        cell_w, cell_h = cell_surface.get_size()

        def is_extra_cell_present(row_offset: int, col_offset: int) -> bool:
            extra_row: int = row + row_offset
            extra_col: int = col + col_offset
            if extra_row >= len(self._cells) or extra_row < 0:
                return False

            if extra_col >= len(self._cells[0]) or extra_col < 0:
                return False

            return (extra_row, extra_col) in cage

        is_left_present: bool = Direction.LEFT in neighbours
        is_right_present: bool = Direction.RIGHT in neighbours
        is_up_present: bool = Direction.UP in neighbours
        is_down_present: bool = Direction.DOWN in neighbours

        # bottom left corner
        if is_down_present and is_left_present and not is_extra_cell_present(1, -1):
            draw.line(cell_surface, self._theme.foreground_primary,
                      Vector2(CAGE_PAD, cell_h), Vector2(CAGE_PAD, cell_h - CAGE_PAD))
            draw.line(cell_surface, self._theme.foreground_primary,
                      Vector2(CAGE_PAD, cell_h - CAGE_PAD), Vector2(0, cell_h - CAGE_PAD))

        # bottom right corner
        if is_down_present and is_right_present and not is_extra_cell_present(1, 1):
            draw.line(cell_surface, self._theme.foreground_primary,
                      cell_size - Vector2(CAGE_PAD, 0), cell_size - Vector2(CAGE_PAD))
            draw.line(cell_surface, self._theme.foreground_primary,
                      cell_size - Vector2(CAGE_PAD), cell_size - Vector2(0, CAGE_PAD))

        # top left corner
        if is_up_present and is_left_present and not is_extra_cell_present(-1, -1):
            draw.line(cell_surface, self._theme.foreground_primary,
                      Vector2(CAGE_PAD, 0), Vector2(CAGE_PAD, CAGE_PAD))
            draw.line(cell_surface, self._theme.foreground_primary,
                      Vector2(CAGE_PAD, CAGE_PAD), Vector2(0, CAGE_PAD))

        # top right corner
        if is_up_present and is_right_present and not is_extra_cell_present(-1, 1):
            draw.line(cell_surface, self._theme.foreground_primary,
                      Vector2(cell_w - CAGE_PAD, 0), Vector2(cell_w - CAGE_PAD, CAGE_PAD))
            draw.line(cell_surface, self._theme.foreground_primary,
                      Vector2(cell_w - CAGE_PAD, CAGE_PAD), Vector2(cell_w, CAGE_PAD))

    def _draw_cage_side(self, row: int, col: int, excluded_directions: set[Direction]) -> None:
        cell_surface: Surface = self._cells[row][col].region.surface
        is_left_present: bool = Direction.LEFT in excluded_directions
        is_right_present: bool = Direction.RIGHT in excluded_directions
        is_up_present: bool = Direction.UP in excluded_directions
        is_down_present: bool = Direction.DOWN in excluded_directions
        start = end = Vector2(0)

        if not is_up_present:
            if not is_left_present and not is_right_present:
                start = Vector2(CAGE_PAD)
                end = Vector2(cell_surface.get_width() - CAGE_PAD, CAGE_PAD)

            elif is_left_present and is_right_present:
                start = Vector2(0, CAGE_PAD)
                end = Vector2(cell_surface.get_width(), CAGE_PAD)

            elif is_right_present:
                start = Vector2(CAGE_PAD)
                end = Vector2(cell_surface.get_width(), CAGE_PAD)

            elif is_left_present:
                start = Vector2(0, CAGE_PAD)
                end = Vector2(cell_surface.get_width() - CAGE_PAD, CAGE_PAD)

            draw.line(cell_surface, self._theme.foreground_primary, start, end)

        if not is_down_present:
            if not is_left_present and not is_right_present:
                start = Vector2(CAGE_PAD, cell_surface.get_height() - CAGE_PAD)
                end = Vector2(cell_surface.get_width() - CAGE_PAD, cell_surface.get_height() - CAGE_PAD)

            elif is_left_present and is_right_present:
                start = Vector2(0, cell_surface.get_height() - CAGE_PAD)
                end = Vector2(cell_surface.get_width(), cell_surface.get_height() - CAGE_PAD)

            elif is_right_present:
                start = Vector2(CAGE_PAD, cell_surface.get_height() - CAGE_PAD)
                end = Vector2(cell_surface.get_width(), cell_surface.get_height() - CAGE_PAD)

            elif is_left_present:
                start = Vector2(0, cell_surface.get_height() - CAGE_PAD)
                end = Vector2(cell_surface.get_width() - CAGE_PAD, cell_surface.get_height() - CAGE_PAD)

            draw.line(cell_surface, self._theme.foreground_primary, start, end)

        if not is_left_present:
            if not is_down_present and not is_up_present:
                start = Vector2(CAGE_PAD)
                end = Vector2(CAGE_PAD, cell_surface.get_height() - CAGE_PAD)

            elif is_down_present and is_up_present:
                start = Vector2(CAGE_PAD, 0)
                end = Vector2(CAGE_PAD, cell_surface.get_height())

            elif is_down_present:
                start = Vector2(CAGE_PAD)
                end = Vector2(CAGE_PAD, cell_surface.get_height())

            elif is_up_present:
                start = Vector2(CAGE_PAD, 0)
                end = Vector2(CAGE_PAD, cell_surface.get_height() - CAGE_PAD)

            draw.line(cell_surface, self._theme.foreground_primary, start, end)

        if not is_right_present:
            if not is_down_present and not is_up_present:
                start = Vector2(cell_surface.get_width() - CAGE_PAD, CAGE_PAD)
                end = Vector2(cell_surface.get_width() - CAGE_PAD, cell_surface.get_height() - CAGE_PAD)

            elif is_down_present and is_up_present:
                start = Vector2(cell_surface.get_width() - CAGE_PAD, 0)
                end = Vector2(cell_surface.get_height() - CAGE_PAD, cell_surface.get_width())

            elif is_down_present:
                start = Vector2(cell_surface.get_width() - CAGE_PAD, CAGE_PAD)
                end = Vector2(cell_surface.get_width() - CAGE_PAD, cell_surface.get_height())

            elif is_up_present:
                start = Vector2(cell_surface.get_width() - CAGE_PAD, 0)
                end = Vector2(cell_surface.get_width() - CAGE_PAD, cell_surface.get_height() - CAGE_PAD)

            draw.line(cell_surface, self._theme.foreground_primary, start, end)

    def _get_collision_offset(self) -> Vector2:
        return Vector2(self.parent.placement.topleft) + \
            Vector2(self._surface.get_rect(center=self.parent.surface.get_rect().center).topleft)

    def _set_selected(self) -> None:
        for cell in chain.from_iterable(self._cells):
            if cell.region.is_collided(self._get_collision_offset()):
                self._selected = cell

    def _render_selected(self) -> None:
        if self._selected is None:
            return

        row_start: int = (self._selected.row // 3) * 3
        col_start: int = (self._selected.col // 3) * 3

        cells_to_render: set[Cell] = set()
        selected_cell: Cell = self._cells[self._selected.row][self._selected.col]

        def require_render(cell_to_render: Cell) -> None:
            if cell_to_render in cells_to_render:
                return
            cells_to_render.add(cell_to_render)

        for cells_row in self._cells:
            for cell in cells_row:

                if cell.row == self._selected.row:
                    require_render(cell)

                elif cell.col == self._selected.col:
                    require_render(cell)

                val: int = self._state[cell.row][cell.col]
                if val != 0 and val == self._state[self._selected.row][self._selected.col]:
                    require_render(cell)

        for row in range(row_start, row_start + 3):
            for col in range(col_start, col_start + 3):
                require_render(self._cells[row][col])

        for cell in cells_to_render:
            cell.region.render_hover()

        selected_cell.region.render_hover()

    def _draw_board_vals(self) -> None:
        font: Font = SysFont(get_fonts()[0], 20)
        for cell in chain.from_iterable(self._cells):
            if (val := self._state[cell.row][cell.col]) == 0:
                continue

            dig: Surface = font.render(str(val), True, self._theme.foreground_primary,
                                       self._theme.background_primary)

            cell.region.surface.blit(dig, dig.get_rect(center=cell.region.surface.get_rect().center))
