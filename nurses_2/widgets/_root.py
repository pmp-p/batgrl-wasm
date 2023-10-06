"""
Root widget.
"""
import numpy as np

from .widget import ColorPair, Point, Region, Size, Widget, style_char

USE_PAINTERS = True


class _Root(Widget):
    """
    Root widget of the widget tree.

    Instantiated only by :class:`nurses_2.app.App`.
    """

    def __init__(
        self, background_char: str, background_color_pair: ColorPair, size: Size
    ):
        self.children = []
        self.background_char = background_char
        self.background_color_pair = background_color_pair
        self._size = size
        self.on_size()

    def on_size(self):
        """
        Erase last render and re-make buffers.
        """
        h, w = self._size

        self.canvas = np.full((h, w), style_char(self.background_char))
        self.colors = np.full((h, w, 6), self.background_color_pair, dtype=np.uint8)

        self._last_canvas = self.canvas.copy()
        self._last_colors = self.colors.copy()

        self._resized = True

    @property
    def pos(self):
        return Point(0, 0)

    @property
    def absolute_pos(self):
        return Point(0, 0)

    @property
    def is_transparent(self):
        return False

    @property
    def is_visible(self):
        return True

    @property
    def is_enabled(self):
        return True

    @property
    def parent(self):
        return None

    @property
    def root(self):
        return self

    def to_local(self, point: Point) -> Point:
        return point

    def collides_point(self, point: Point) -> bool:
        y, x = point
        return 0 <= y < self.height and 0 <= x < self.width

    def render(self):
        """
        Render widget tree into `canvas` and `colors`.
        """
        # TODO: Optimize...
        # - Recalculating all regions every frame isn't necessary if widget geometry
        #   hasn't changed.
        # - If there *is* a change to geometry, regions that are later in z-order can be
        #   reused.
        # - Checking for changes in geometry can be done once every few frames if
        #   geometry has been static for some time.
        self.region = Region.from_rect(self.pos, self.size)

        for child in self.walk():
            child.region = (
                child.parent.region & Region.from_rect(child.absolute_pos, child.size)
                if child.is_enabled
                else Region()
            )

        for child in self.walk_reverse():
            if child.is_enabled:
                child.region &= self.region
                if child.is_visible and not child.is_transparent:
                    self.region -= child.region

        self.canvas, self._last_canvas = self._last_canvas, self.canvas
        self.colors, self._last_colors = self._last_colors, self.colors

        self.canvas[:] = style_char(self.background_char)
        self.colors[:] = self.background_color_pair

        for child in self.walk():
            if child.is_enabled and child.is_visible:
                child.render(self.canvas, self.colors)
