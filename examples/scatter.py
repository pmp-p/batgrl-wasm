"""
Scatter and DraggableBehavior both inherit from GrabbableBehavior, but what
happens if you want a draggable Scatter? Exactly what you'd expect!
"""
import asyncio

import numpy as np

from nurses_2.app import App
from nurses_2.colors import BLUE, GREEN, WHITE, gradient, ColorPair
from nurses_2.widgets.behaviors.draggable_behavior import DraggableBehavior
from nurses_2.widgets.text_widget import TextWidget
from nurses_2.widgets.scatter import Scatter

WHITE_ON_GREEN = ColorPair.from_colors(WHITE, GREEN)
WHITE_ON_BLUE = ColorPair.from_colors(WHITE, BLUE)


class DraggableScatter(DraggableBehavior, Scatter):
    ...


class PrettyWidget(TextWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        grad = gradient(WHITE_ON_GREEN, WHITE_ON_BLUE, (self.width >> 1) - 2)

        self.colors[:] = 50
        self.colors[1:-1, 2:-2] = grad + grad[::-1]

        asyncio.create_task(self.roll())

    async def roll(self):
        while True:
            self.colors[1:-1, 2:-2] = np.roll(self.colors[1:-1, 2:-2], -1, (1, ))

            await asyncio.sleep(.11)


class MyApp(App):
    async def on_start(self):
        widget_1 = PrettyWidget(size=(20, 40))
        widget_2 = PrettyWidget(size=(10, 50))

        draggable_scatter = DraggableScatter(size=(30, 100), default_color_pair=25)
        draggable_scatter.add_widgets(widget_1, widget_2)

        self.add_widget(draggable_scatter)


MyApp().run()
