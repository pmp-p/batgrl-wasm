import asyncio

import numpy as np

from nurses_2.app import App
from nurses_2.colors import Color, ColorPair, BLACK, WHITE_ON_BLACK
from nurses_2.io import MouseButton
from nurses_2.widgets.text_widget import TextWidget
from nurses_2.widgets.graphic_widget import GraphicWidget, Anchor
from nurses_2.widgets.slider import Slider

from .solver import SPHSolver

WATER_COLOR = Color.from_hex("1e1ea8")
FILL_COLOR = Color.from_hex("2fa399")
WATER_ON_BLACK = ColorPair.from_colors(WATER_COLOR, BLACK)


class SPH(GraphicWidget):
    def __init__(self, nparticles, is_transparent=False, **kwargs):
        super().__init__(is_transparent=is_transparent, **kwargs)
        y, x = self.size
        self.sph_solver = SPHSolver(nparticles, (2 * y, x))

    def on_add(self):
        super().on_add()
        self._update_task = asyncio.create_task(self._update())

    def on_remove(self):
        super().on_remove()
        self._update_task.cancel()

    def on_key(self, key_event):
        match key_event.key:
            case "r":
                self.sph_solver.init_dam()
                return True

        return False

    def on_mouse(self, mouse_event):
        if (
            mouse_event.button is MouseButton.NO_BUTTON
            or not self.collides_point(mouse_event.position)
        ):
            return False

        # Apply a force from click to every particle in the solver.
        my, mx = self.to_local(mouse_event.position)

        relative_positions = self.sph_solver.state[:, :2] - (2 * my, mx)

        self.sph_solver.state[:, 2:4] += (
            1e2 * relative_positions
            / np.linalg.norm(relative_positions, axis=-1, keepdims=True)
        )

        return True

    async def _update(self):
        while True:
            solver = self.sph_solver
            solver.step()

            positions = solver.state[:, :2]

            ys, xs = positions.astype(int).T
            xs = xs + (self.width - solver.WIDTH) // 2  # Center the particles.

            # Some solver configurations are unstable. Clip positions to prevent errors.
            ys = np.clip(ys, 0, 2 * self.height - 1)
            xs = np.clip(xs, 0, self.width - 1)

            self.texture[:] = self.default_color
            self.texture[ys, xs, :3] = WATER_COLOR

            await asyncio.sleep(0)


class SPHApp(App):
    async def on_start(self):
        height, width = 26, 51
        slider_settings = (
            ("H", "Smoothing Length", .4, 3.5),
            ("GAS_CONST", "Gas Constant", 500.0, 4000.0),
            ("REST_DENS", "Rest Density", 150.0, 500.0),
            ("VISC", "Viscosity", 0.0, 5000.0),
            ("MASS", "Mass", 10.0, 500.0),
            ("DT", "DT", .001, .03),
            ("GRAVITY", "Gravity", 0.0, 1e5),
            ("WIDTH", "Width", 5, width),
        )
        sliders_height = (len(slider_settings) + 1) // 2 * 2

        container = TextWidget(
            size=(height, width),
            pos_hint=(.5, .5),
            anchor=Anchor.CENTER,
            default_color_pair=WHITE_ON_BLACK,
        )

        fluid = SPH(
            nparticles=225,
            pos=(sliders_height, 0),
            size=(height - sliders_height, width),
        )

        def create_callback(caption, attr, y, x):
            def update(value):
                setattr(fluid.sph_solver, attr, value)
                if isinstance(v := getattr(fluid.sph_solver, attr), int):
                    value = f"{v}"
                else:
                    value = f"{v:.4}"
                container.add_str(f"{caption}: {value}".ljust(width // 2), (y, x))
            return update

        container.add_widget(fluid)
        for i, (attr, caption, min, max) in enumerate(slider_settings):
            y = i // 2 * 2
            x = (i % 2) * (width // 2 + 1)
            container.add_widget(
                Slider(
                    pos=(y + 1, x),
                    min=min,
                    max=max,
                    start_value=getattr(fluid.sph_solver, attr),
                    callback=create_callback(caption, attr, y, x),
                    size=(1, width // 2),
                    fill_color=FILL_COLOR,
                    default_color_pair=WATER_ON_BLACK,
                )
            )
        self.add_widget(container)


SPHApp(title="Smoothed-Particle Hydrodynamics").run()
