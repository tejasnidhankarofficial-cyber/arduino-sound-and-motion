from image import Image
from media import Media


class Animation(Media):
    """A sequence of 8x12 frames, played one after another on the LED matrix.

    Each frame is stored separately because grid_to_hexLine() converts one frame at a time.
    """

    def __init__(self, mediaId, name, artist, frames, count=0):
        super().__init__(mediaId, name, artist, count)
        self.frames = frames

    # ---------- frames (list of 8x12 grids) ----------
    @property
    def frames(self):
        return [[row[:] for row in frame] for frame in self.__frames]

    @frames.setter
    def frames(self, value):
        if len(value) == 0:
            raise ValueError("an animation needs at least one frame")
        self.__frames = [Image.validateGrid(frame) for frame in value]

    def numFrames(self):
        return len(self.__frames)

    # ---------- special methods ----------
    def __str__(self):
        """Display the first frame of the animation."""
        return Image.gridToString(self.__frames[0])
