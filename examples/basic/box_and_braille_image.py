from pathlib import Path

from nurses_2.app import App
from nurses_2.widgets.box_image import BoxImage
from nurses_2.widgets.braille_image import BrailleImage

ASSETS = Path(__file__).parent.parent / "assets"
PATH_TO_IMAGE = ASSETS / "loudypixelsky.png"


class ImageApp(App):
    async def on_start(self):
        box_image = BoxImage(path=PATH_TO_IMAGE, size_hint=(1.0, .5))
        braille_image = BrailleImage(path=PATH_TO_IMAGE, size_hint=(1.0, .5), pos_hint=(None, .5))
        self.add_widgets(box_image, braille_image)


ImageApp(title="Box and Braille Image Example").run()
