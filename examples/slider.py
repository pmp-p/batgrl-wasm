"""
Example slider widget.
"""
import asyncio

from nurses_2.app import App
from nurses_2.colors import BLUE, GREEN, BLACK, color_pair
from nurses_2.widgets import Widget
from nurses_2.widgets.slider import Slider

GREEN_ON_BLACK = color_pair(GREEN, BLACK)


class MyApp(App):
    async def on_start(self):
        display = Widget(size=(2, 30))
        display.add_text("Slider 1 Value:", row=0)
        display.add_text("Slider 2 Value:", row=1)

        slider_1 = Slider(
            width=20,
            pos=(2, 0),
            min=0,
            max=100,
            handle_color=BLUE,
            callback=lambda value: display.add_text(f"{value:<10}", row=0, column=16),
            default_color_pair=GREEN_ON_BLACK,
        )
        slider_2 = Slider(
            width=15,
            pos=(3, 0),
            min=-20,
            max=50,
            handle_color=BLUE,
            callback=lambda value: display.add_text(f"{value:<10}", row=1, column=16),
            default_color_pair=GREEN_ON_BLACK,
        )
        self.root.add_widgets(display, slider_1, slider_2)


MyApp().run()
