class Media:
    """Superclass for every kind of media the Arduino can output.

    Holds only what Image, Animation and Audio all have in common:
    an id, a name, an artist and how many times it has been played/displayed.
    The media type is NOT stored - the subclass an object belongs to already says it.
    """

    def __init__(self, mediaId, name, artist, count=0):
        # Go through the setters so the constructor uses the same validation.
        self.id = mediaId
        self.name = name
        self.artist = artist
        self.count = count

    # ---------- id ----------
    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ValueError(f"id must be a positive integer, got {value!r}")
        self.__id = value

    # ---------- name ----------
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = Media._requireText(value, "name")

    # ---------- artist ----------
    @property
    def artist(self):
        return self.__artist

    @artist.setter
    def artist(self, value):
        self.__artist = Media._requireText(value, "artist")

    # ---------- count ----------
    @property
    def count(self):
        """How many times this media has been sent to the Arduino."""
        return self.__count

    @count.setter
    def count(self, value):
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"count must be a non-negative integer, got {value!r}")
        self.__count = value

    def incrementCount(self):
        """Call this each time the media is sent to the Arduino."""
        self.__count += 1

    # ---------- special methods ----------
    def __str__(self):
        # Subclasses override this to show their own content.
        return f"{self.__name} by {self.__artist}"

    # ---------- helpers ----------
    @staticmethod
    def _requireText(value, field):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string, got {value!r}")
        return value.strip()
