from itertools import product

import numpy as np
import cv2

from nurses_2.io import MouseButton, MouseEventType

from .colors import *
from .grid import Grid
from .unicode_chars import FLAG


class Minefield(Grid):
    """
    A grid that becomes transparent when clicked revealing the counts underneath.
    """
    def __init__(self, count, minefield, **kwargs):
        super().__init__(
            size=count.shape,
            is_light=False,
            default_color_pair=HIDDEN,
            **kwargs,
        )
        self.count = count
        self.minefield = minefield
        self.nmines = minefield.sum()
        self._is_gameover = False

        vs, hs = self.V_SPACING, self.H_SPACING
        v_center, h_center = self.cell_center_indices

        self.colors[v_center, h_center, :3] = FLAG_COLOR

        # Build an array whose zero values indicate revealed areas.
        kernel = np.ones((vs + 1, hs + 1), dtype=np.uint8)
        squares = np.zeros(self.size, dtype=np.uint8)
        squares[v_center, h_center] = 1

        self.hidden = cv2.filter2D(squares, -1, kernel, borderType=cv2.BORDER_CONSTANT)
        self.hidden_cells = self.hidden[v_center, h_center]

        self._pressed_cell = self._pressed_button = None

    def on_mouse(self, mouse_event):
        position, event_type, button, _, _ = mouse_event

        if event_type not in (MouseEventType.MOUSE_DOWN, MouseEventType.MOUSE_UP):
            return False

        if not self.collides_point(position):
            if event_type == MouseEventType.MOUSE_UP and self._pressed_cell:
                self._release()

            return False

        if event_type == MouseEventType.MOUSE_DOWN:
            if self._pressed_cell:
                self._release()

            self._pressed_cell = self._cell_from_pos(position)
            self._pressed_button = button

            if button == MouseButton.LEFT:
                self._normal_press()
            elif button == MouseButton.RIGHT:
                self._flag_press()
            elif button == MouseButton.MIDDLE:
                self._super_press()
            else:
                return False

        else:  # MOUSE_UP
            if not self._pressed_cell:
                return False

            if (
                self._cell_from_pos(position) == self._pressed_cell
                and self._pressed_button in (MouseButton.LEFT, MouseButton.MIDDLE)
            ):
               self.reveal_cell(self._pressed_cell, reveal_neighbors=self._pressed_button == MouseButton.MIDDLE)

            self._release()

        return True

    def _cell_from_pos(self, mouse_position):
        """
        Return the cell-coordinates cooresponding to given mouse position.
        """
        y, x = self.to_local(mouse_position)

        if y == self.height - 1:
            y -= 1

        if x == self.width - 1:
            x -= 1

        return y // self.V_SPACING, x // self.H_SPACING

    def _cell_center(self, cell):
        """
        A cell's center in grid-coordinates.
        """
        y, x = cell
        vs, hs = self.V_SPACING, self.H_SPACING

        return y * vs + vs // 2, x * hs + hs // 2

    def _cell_slice(self, cell):
        """
        Return a tuple of slices that indicate a cell's rect in the grid.
        """
        y, x = cell

        vs, hs = self.V_SPACING, self.H_SPACING
        j, i = y * vs, x * hs

        return slice(j, j + vs + 1), slice(i, i + hs + 1)

    def _recolor_cell(self, cell, color_pair):
        self.colors[self._cell_slice(cell)] = color_pair

        u, v = self._cell_center(cell)
        self.colors[u, v, :3] = FLAG_COLOR

    def _neighbors(self, cell):
        y, x = cell
        h, w = self.minefield.shape

        for j, i in product((-1, 0, 1), repeat=2):
            if j == i == 0:
                continue

            v, u = j + y, i + x
            # Bounds check
            if v < 0 or v >= h or u < 0 or u >= w:
                continue

            yield v, u

    def is_flagged(self, cell):
        return self.canvas["char"][self._cell_center(cell)] == FLAG

    def _normal_press(self):
        if not self._is_gameover:
            self.parent.reset_button.update_down()

        cell = self._pressed_cell

        if self.hidden_cells[cell] != 0 and not self.is_flagged(cell):
            self._recolor_cell(cell, HIDDEN_REVERSED)

    def _flag_press(self):
        cell = self._pressed_cell

        if self.hidden_cells[cell] != 0:
            is_flagged = self.is_flagged(cell)

            self.canvas["char"][self._cell_center(cell)] = " " if is_flagged else FLAG
            self.parent.mines += 1 if is_flagged else -1

    def _super_press(self):
        if not self._is_gameover:
            self.parent.reset_button.update_down()

        cell = self._pressed_cell

        if self.hidden_cells[cell] != 0 and not self.is_flagged(cell):
            self._recolor_cell(cell, HIDDEN_REVERSED)

        for neighbor in self._neighbors(cell):
            if self.hidden_cells[neighbor] != 0 and not self.is_flagged(neighbor):
                self._recolor_cell(neighbor, HIDDEN_REVERSED)

    def _release(self):
        if not self._is_gameover:
            self.parent.reset_button.update_normal()

        cell = self._pressed_cell

        self._recolor_cell(cell, HIDDEN)

        if self._pressed_button == MouseButton.MIDDLE:
            for neighbor in self._neighbors(cell):
                self._recolor_cell(neighbor, HIDDEN)

        self._pressed_cell = self._pressed_button = None

    def reveal_cell(self, cell, reveal_neighbors: bool):
        if reveal_neighbors:
            adjacent_flags = sum(map(self.is_flagged, self._neighbors(cell)))

            if self.hidden_cells[cell] == 0 and self.count[cell] != adjacent_flags:
                return

            for neighbor in self._neighbors(cell):
                self.reveal_cell(neighbor, reveal_neighbors=False)

        if self.hidden_cells[cell] == 0 or self.is_flagged(cell):
            return

        if self.minefield[cell]:
            self._game_over(win=False)
            return

        self.hidden[self._cell_slice(cell)] -= 1

        if self.count[cell] == 0:
            for neighbor in self._neighbors(cell):
                self.reveal_cell(neighbor, reveal_neighbors=False)

        if self.hidden_cells.sum() == self.nmines:
            self._game_over(win=True)
            return

    def _game_over(self, win: bool):
        self.hidden[:] = 0
        self._is_gameover = True
        self.parent.game_over(win=win)

    def render(self, canvas_view, colors_view, source: tuple[slice, slice]):
        canvas_source = self.canvas[source]
        visible = self.hidden[source] != 0

        canvas_view[visible] = canvas_source[visible]
        colors_view[visible] = self.colors[source][visible]

        self.render_children(source, canvas_view, colors_view)
