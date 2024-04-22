from dataclasses import dataclass
from enum import Enum
from enum import auto
from functools import cache
from itertools import chain
from queue import Queue
from time import time
from typing import Optional
from typing import override

from pygame import BUTTON_LEFT
from pygame import Color
from pygame import K_LCTRL
from pygame import MOUSEBUTTONDOWN
from pygame import MOUSEBUTTONUP
from pygame import draw
from pygame import key
from pygame import mouse
from pygame.event import Event
from pygame.font import Font
from pygame.font import SysFont
from pygame.font import get_fonts
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from config.app_config import BOARD_SIZE
from config.app_config import DOUBLE_CLICK_DELAY
from config.game_config import CAGE_PAD
from config.game_config import CELL_PAD
from config.game_config import SUM_FONT_SIZE
from events import AppEvent
from gui_component import GuiComponent
from killer_sudoku_state import KillerSudokuState
from region import Region
from themes import AppTheme


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

    def __init__(self, cell_region: Region, row: int, col: int) -> None:
        self.region: Region = cell_region
        self.row: int = row
        self.col: int = col


class Selection:

    def __init__(self) -> None:
        self.selected: set[Cell] = set()
        self.selecting: bool = False

    def add_cell(self, cell: Cell) -> None:
        if cell in self.selected:
            return

        self.selected.add(cell)

    def get_single_selection(self) -> Optional[Cell]:
        if len(self.selected) != 1:
            return None

        return list(self.selected)[0]

    def clear(self) -> None:
        self.selected = set()

    def get_selection_sum(self, state: KillerSudokuState) -> int:
        selection_sum: int = 0

        if len(self.selected) == 0:
            return selection_sum

        selected_index: set[tuple[int, int]] = {(cell.row, cell.col) for cell in self.selected}
        for val, cage in state.puzzle.cages:
            if len(selected_index.intersection(cage)) == len(cage):
                selection_sum += val
                selected_index -= set(cage)

        for row, col in selected_index:
            cell_val: int = state[row][col]
            if cell_val == 0:
                return 0

            else:
                selection_sum += cell_val

        return selection_sum


class PencilMarksDisplay:

    def __init__(self, cell_size: Rect, theme: AppTheme, font_name: str) -> None:
        self.surface: Surface = Surface(Vector2(cell_size.size) - Vector2((CAGE_PAD + 2) * 2))
        self.regions: list[Region] = self._create_regions(theme)

        self._font_name: str = font_name
        self._font_size: int = self._calculate_font_size()

    def redraw(self, theme: AppTheme) -> None:
        self.regions = self._create_regions(theme)
        self._font_size = self._calculate_font_size()

    def get_font(self) -> Font:
        return SysFont(self._font_name, self._font_size)

    def _calculate_font_size(self) -> int:
        font_size: int = 1
        bounding_box: Rect = self.regions[0].surface.get_rect()
        while True:
            font: Font = SysFont(self._font_name, font_size)
            size: Vector2 = Vector2(font.size("0"))
            if size.x > bounding_box.width:
                return font_size - 1

            if size.y > bounding_box.height:
                return font_size - 1

            font_size += 1

    def _create_regions(self, theme: AppTheme) -> list[Region]:
        regions: list[Region] = []
        prev_placement: Optional[Rect] = None
        first_placement: Optional[Rect] = None
        size: Vector2 = Vector2(self.surface.get_size()) // 3
        for row in range(3):
            for col in range(3):
                surface: Surface = Surface(size)
                surface.fill(theme.background)
                placement: Rect = surface.get_rect(topleft=(0, 0))
                if prev_placement is not None and first_placement is not None:
                    if col == 0:
                        placement = surface.get_rect(topleft=first_placement.bottomleft)
                    else:
                        placement = surface.get_rect(topleft=prev_placement.topright)

                prev_placement = placement
                if col == 0:
                    first_placement = placement

                regions.append(Region(self.surface, surface, placement))

        return regions


@dataclass
class DoubleClickInfo:
    _prev_click: Optional[float] = None

    def click(self) -> bool:
        result: bool = False
        now: float = time()
        update: bool = True
        if self._prev_click is not None:
            if now - self._prev_click < DOUBLE_CLICK_DELAY:
                update = False
                result = True
                self._prev_click = None

        if update:
            self._prev_click = now

        return result


class BoardGui(GuiComponent):
    @override
    def render(self) -> None:
        for cell in chain.from_iterable(self._cells):
            cell.region.render()

        if self._require_redraw:
            self._clear_cells()
            self._draw_pencil_marks()
            self._draw_board_vals()
            self._draw_cages()
            self._require_redraw = False

        for cell in self.selection.selected:
            cell.region.render_hover()

        self.parent.surface.blit(self._surface,
                                 self._surface.get_rect(center=self.parent.surface.get_rect().center))
        self.parent.render()

    @override
    def update(self, delta_time: float) -> None:
        if not self.selection.selecting:
            return

        for cell in chain.from_iterable(self._cells):
            if cell.region.is_collided(self._get_collision_offset()):
                self.selection.add_cell(cell)

    @override
    def update_theme(self) -> None:
        self.parent.surface.fill(self._theme.background)
        self._surface.fill(self._theme.foreground)
        for cell in chain.from_iterable(self._cells):
            cell.region.surface.fill(self._theme.background)
            cell.region.set_hover_color(self._theme.foreground)

        self._pencil_marks.redraw(self._theme)

    @override
    def parse_event(self, game_event: Event, events: Queue[AppEvent]) -> None:
        if not self.parent.placement.collidepoint(mouse.get_pos()):
            self.selection.selecting = False
            return

        if game_event.type == MOUSEBUTTONUP:
            if game_event.button == BUTTON_LEFT:
                self.selection.selecting = False

        elif game_event.type == MOUSEBUTTONDOWN:
            if game_event.button == BUTTON_LEFT:
                if self._double_click.click():
                    self._select_equal_values()

                else:
                    if len(self.selection.selected) > 0 and not key.get_pressed()[K_LCTRL]:
                        self.selection.clear()

                    self.selection.selecting = True

    def __init__(self, parent: Region, theme: AppTheme, state: KillerSudokuState) -> None:
        super().__init__(parent, theme)
        self._state: KillerSudokuState = state
        self._cells: list[list[Cell]] = []
        self._surface: Surface = self._create_board_surface()
        self._require_redraw: bool = True
        self._pencil_marks: PencilMarksDisplay = PencilMarksDisplay(self._cells[0][0].region.surface.get_rect(), theme,
                                                                    get_fonts()[0])
        self.selection: Selection = Selection()
        self._double_click: DoubleClickInfo = DoubleClickInfo()

    @property
    def require_redraw(self) -> bool:
        return self._require_redraw

    @require_redraw.setter
    def require_redraw(self, redraw: bool) -> None:
        self._require_redraw = redraw

    @require_redraw.deleter
    def require_redraw(self) -> None:
        del self._require_redraw

    def _select_equal_values(self) -> None:
        if (selected := self.selection.get_single_selection()) is None:
            return

        if (selected_val := self._state[selected.row][selected.col]) == 0:
            return

        self.selection.clear()
        for cell in chain.from_iterable(self._cells):
            if self._state[cell.row][cell.col] == selected_val:
                self.selection.add_cell(cell)

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

    def _draw_pencil_marks(self) -> None:
        for cell in chain.from_iterable(self._cells):
            self._pencil_marks.surface.fill(self._theme.background)

            if self._state[cell.row][cell.col] != 0:
                continue

            if not (markings := self._state.get_pencil_markings(cell.row, cell.col)):
                continue

            for region, mark in zip(self._pencil_marks.regions, markings):
                is_mark_valid: bool = self._state.is_mark_valid(mark, cell.row, cell.col)
                font_color: Color = self._theme.foreground \
                    if is_mark_valid else self._theme.invalid
                val: Surface = self._pencil_marks.get_font().render(str(mark), True, font_color,
                                                                    self._theme.background)
                region.surface.blit(val, val.get_rect(center=region.surface.get_rect().center))
                region.render()

            cell.region.surface.blit(self._pencil_marks.surface,
                                     self._pencil_marks.surface.get_rect(center=cell.region.surface.get_rect().center))

    def _draw_cages(self) -> None:
        font: Font = SysFont(get_fonts()[0], SUM_FONT_SIZE)
        for cage_sum, cells in self._state.puzzle.cages:
            present_cells: set[tuple[int, int]] = set(cells)
            sum_row, sum_col = cells[-1]
            sum_cell: Cell = self._cells[sum_row][sum_col]

            is_cage_valid: bool = self._state.is_cage_valid(cage_sum, cells)
            line_color = self._theme.foreground if is_cage_valid else self._theme.invalid
            sum_surface: Surface = font.render(str(cage_sum), True, line_color, self._theme.background)
            for row, col in cells:
                neighbours: set[Direction] = self._get_present_neighbours(row, col, present_cells)
                self._draw_cage_side(row, col, neighbours, line_color)
                self._draw_cage_corner(row, col, neighbours, cells, line_color)

            sum_cell.region.surface.blit(sum_surface, sum_surface.get_rect(center=(CAGE_PAD, CAGE_PAD)))

    def _draw_cage_corner(self, row: int, col: int, neighbours: set[Direction], cage: list[tuple[int, int]],
                          line_color: Color) -> None:
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
            draw.line(cell_surface, line_color,
                      Vector2(CAGE_PAD, cell_h), Vector2(CAGE_PAD, cell_h - CAGE_PAD))
            draw.line(cell_surface, line_color,
                      Vector2(CAGE_PAD, cell_h - CAGE_PAD), Vector2(0, cell_h - CAGE_PAD))

        # bottom right corner
        if is_down_present and is_right_present and not is_extra_cell_present(1, 1):
            draw.line(cell_surface, line_color,
                      cell_size - Vector2(CAGE_PAD, 0), cell_size - Vector2(CAGE_PAD))
            draw.line(cell_surface, line_color,
                      cell_size - Vector2(CAGE_PAD), cell_size - Vector2(0, CAGE_PAD))

        # top left corner
        if is_up_present and is_left_present and not is_extra_cell_present(-1, -1):
            draw.line(cell_surface, line_color,
                      Vector2(CAGE_PAD, 0), Vector2(CAGE_PAD, CAGE_PAD))
            draw.line(cell_surface, line_color,
                      Vector2(CAGE_PAD, CAGE_PAD), Vector2(0, CAGE_PAD))

        # top right corner
        if is_up_present and is_right_present and not is_extra_cell_present(-1, 1):
            draw.line(cell_surface, line_color,
                      Vector2(cell_w - CAGE_PAD, 0), Vector2(cell_w - CAGE_PAD, CAGE_PAD))
            draw.line(cell_surface, line_color,
                      Vector2(cell_w - CAGE_PAD, CAGE_PAD), Vector2(cell_w, CAGE_PAD))

    def _draw_cage_side(self, row: int, col: int, excluded_directions: set[Direction], line_color: Color) -> None:
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

            draw.line(cell_surface, line_color, start, end)

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

            draw.line(cell_surface, line_color, start, end)

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

            draw.line(cell_surface, line_color, start, end)

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

            draw.line(cell_surface, line_color, start, end)

    def _get_collision_offset(self) -> Vector2:
        return Vector2(self.parent.placement.topleft) + \
            Vector2(self._surface.get_rect(center=self.parent.surface.get_rect().center).topleft)

    def _clear_cells(self) -> None:
        for cell in chain.from_iterable(self._cells):
            cell.region.surface.fill(self._theme.background)

    def _draw_board_vals(self) -> None:
        font: Font = SysFont(get_fonts()[0], 20)
        for cell in chain.from_iterable(self._cells):
            if (val := self._state[cell.row][cell.col]) == 0:
                continue

            is_value_valid: bool = self._state.is_value_valid(cell.row, cell.col)
            line_color = self._theme.foreground if is_value_valid else self._theme.invalid
            dig: Surface = font.render(str(val), True, line_color, self._theme.background)

            cell.region.surface.blit(dig, dig.get_rect(center=cell.region.surface.get_rect().center))
