from media import Media


class Audio(Media):
    """A song for the piezo buzzer: an ordered list of (pitch, duration) notes.

    pitch    - frequency in Hz (0 means a rest)
    duration - note length as a fraction of a second (4 = quarter note = 250 ms)
    Each pitch stays paired with its own duration, in the order they appear in the file.
    """

    def __init__(self, mediaId, name, artist, notes, count=0):
        super().__init__(mediaId, name, artist, count)
        self.notes = notes

    # ---------- notes (list of (pitch, duration) tuples) ----------
    @property
    def notes(self):
        return list(self.__notes)  # tuples are immutable, so a shallow copy is safe

    @notes.setter
    def notes(self, value):
        if len(value) == 0:
            raise ValueError("a song needs at least one note")
        cleaned = []
        for pitch, duration in value:
            pitch, duration = int(pitch), int(duration)
            if pitch < 0 or duration < 1:
                raise ValueError(f"invalid note: pitch={pitch}, duration={duration}")
            cleaned.append((pitch, duration))
        self.__notes = cleaned

    def numNotes(self):
        return len(self.__notes)

    # ---------- special methods ----------
    def __str__(self):
        """Display every note's pitch, but not its duration."""
        return ", ".join(str(pitch) for pitch, _ in self.__notes)
