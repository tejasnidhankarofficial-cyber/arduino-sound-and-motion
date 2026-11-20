from media import Media


class Image(Media):
    """A single 8x12 picture for the LED matrix."""

    ROWS = 8
    COLS = 12

    def __init__(self, mediaId, name, artist, grid, count=0):
        super().__init__(mediaId, name, artist, count)
        self.grid = grid

    # ---------- grid (8 rows x 12 columns of 0/1) ----------
    @property
    def grid(self):
        # Return a copy so outside code can't change the image without the setter.
        return [row[:] for row in self.__grid]

    @grid.setter
    def grid(self, value):
        self.__grid = Image.validateGrid(value)

    # ---------- special methods ----------
    def __str__(self):
        """Display the image: '#' for an LED that is on, '.' for off."""
        return Image.gridToString(self.__grid)

    # ---------- helpers shared with Animation (its frames are grids too) ----------
    @staticmethod
    def validateGrid(grid):
        """Return a clean copy of grid, or raise ValueError if it is not 8x12 of 0s and 1s."""
        if len(grid) != Image.ROWS:
            raise ValueError(f"expected {Image.ROWS} rows, found {len(grid)}")
        cleaned = []
        for row in grid:
            row = [int(bit) for bit in row]
            if len(row) != Image.COLS or any(bit not in (0, 1) for bit in row):
                raise ValueError(f"each row must be {Image.COLS} values of 0 or 1: {row}")
            cleaned.append(row)
        return cleaned

    @staticmethod
    def gridToString(grid):
        return "\n".join(" ".join("#" if bit else "." for bit in row) for row in grid)
