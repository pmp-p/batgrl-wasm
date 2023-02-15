import wcwidth
import termios
import tty
import numpy
import cv2
import nurses_2
os.chdir("examples/basic")

# BASIC

# OK
# buttons color_picker io_events.py line_plot.py menu.py
# optical_illusion.py progress_bar.py scroll_view.py slider.py
# subscription.py

# NOT
# animations file_chooser easings image parallax.py split_layout.py
# tile.py video_in_terminal.py windows.py shadow_casting.py
# sliding_puzzle.py

os.chdir("../advanced")

# OK
# digital_clock.py doom_fire.py exploding_logo.py game_of_life.py
# isotiles.py navier_stokes.py pong.py reaction_diffusion.py

# NOT
# exploding_logo_redux.py

#?
# labyrinth.py snake.py

for test in "tetris sph sandbox rubiks raycaster minesweeper connect4 cloth".split(' '):
    if test in sys.argv:
        sys.path.append(test)
        exec(f"from {test} import __main__", globals(), globals())
        break

# NOT
# tetris
