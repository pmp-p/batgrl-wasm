import asyncio
import atexit
from pathlib import Path
import time
from typing import Union

import cv2
import numpy as np

from ..colors import BLACK_ON_BLACK
from .graphic_widget import GraphicWidget, Interpolation


# Seeking is not implemented yet, but may get added soon™
class VideoPlayer(GraphicWidget):
    """
    A video player.

    Parameters
    ----------
    source : pathlib.Path | str | int
        A path to video, URL to video stream, or capturing device (by index).
    """
    def __init__(self, *args, source: Union[Path, str, int], **kwargs):
        super().__init__(*args, **kwargs)

        self._resource = None
        self._video = asyncio.create_task(asyncio.sleep(0))  # dummy task

        self.source = source

    @property
    def video(self):
        return self._video

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, new_source):
        self.stop()
        self._source = new_source

    def _load_video(self):
        source = self.source
        if isinstance(source, Path):
            source = str(source)

        self._resource = cv2.VideoCapture(source)
        atexit.register(self._resource.release)

    def close(self):
        if self._resource is not None:
            self._resource.release()

            # `cv2` may write warnings to stdout on Windows when releasing cameras.
            # We force a screen regeneration by calling resize on the root widget.
            self.root.resize(self.root.size)

            atexit.unregister(self._resource.release)
            self._resource = None
            self._current_frame = None
            self.texture[..., :3] = self.default_bg_color
            self.texture[..., 3] = 255

    def resize(self, size):
        super().resize(size)

        # If video is paused, resize current frame.
        if self._video.done() and self._current_frame is not None:
            size = self.width, 2 * self.height
            resized_frame = cv2.resize(self._current_frame, size)
            self.texture[..., :3] = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

    async def _play_video(self):
        # Bring in to locals:
        resize = cv2.resize
        recolor = cv2.cvtColor
        MSEC = cv2.CAP_PROP_POS_MSEC
        BGR2RGB = cv2.COLOR_BGR2RGB
        monotonic = time.monotonic

        video_get = self._resource.get
        video_grab = self._resource.grab
        video_retrieve = self._resource.retrieve

        video_grab()
        start_time = monotonic() - video_get(MSEC) / 1000

        while True:
            if not video_grab():
                break

            seconds_ahead = video_get(MSEC) / 1000 + start_time - monotonic()
            if seconds_ahead < 0:
                continue

            ret_flag, self._current_frame = video_retrieve()
            if not ret_flag:
                break

            size = self.width, 2 * self.height
            resized_frame = resize(self._current_frame, size)
            self.texture[..., :3] = recolor(resized_frame, BGR2RGB)

            try:
                await asyncio.sleep(seconds_ahead)
            except asyncio.CancelledError:
                return

        self.close()

    def play(self):
        """
        Play video.
        """
        if self._resource is None:
            self._load_video()

        self._video.cancel()
        self._video = asyncio.create_task(self._play_video())

    def pause(self):
        """
        Pause video.
        """
        self._video.cancel()

    def stop(self):
        """
        Stop video.
        """
        self.pause()
        self.close()
