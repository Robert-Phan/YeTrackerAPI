from abc import ABC, abstractmethod
import pprint

from yetracker.column import * 
from yetracker.era import *
from yetracker.era import Era

@add_repr
class Entry(ABC):
    @abstractmethod
    def __init__(self, row: Row):
        pass

class WithNames:
    """Base class used to derive various attributes
    from the "Name" column in multiple tabs.
    
    Attributes:
        full_name (str): The full text of the entry's "Name" column.
        main_name (str): The entry's main name.
        alt_names (list[str]): Alternative names the entry is known by.
        emojis (list[Emoji]): The list of Emojis the entry has.
        version (Version | None): The version number of the entry.
        contribs (Contributors): Contributors to the song.
        artist (str | None): The artist of the entry 
            (if not the tracker's main artist)
    """
    def _set_name_attrs(self, row: Row):
        name_column = Name(row, 1)
        self.full_name = name_column()
        self.main_name = name_column.main_name
        self.emojis = name_column.emojis
        self.version = name_column.version
        self.contribs = name_column.contribs
        self.alt_names = name_column.alt_names
        self.artist = name_column.artist

class WithEras:
    """Base class of entries in tabs with specical rows
    for eras and suberas.
    
    Attributes:
        era (str | Era): Either the plain-text name of the era 
            (equivalent to `era_name`),
            or an Era object.
        subera (SubEra | None): The subera of the entry.
    """

    def _set_era_attrs(self, era_name: str):
        self.era: str | Era = era_name
        self.subera: SubEra | None = None

    def set_era(self, era: Era):
        self.era = era

    def set_subera(self, subera: SubEra):
        self.subera = subera

class Song(Entry, WithNames, WithEras):
    """Base class for 'song'-like entries.  
    Inherits attributes from `WithEras`.  
    Inherits attributes from `WithNames`.
    
    Attributes:
        era_name: The plain-text name of the era/album the entry is from.
        notes (str): The entry's notes.
        length (timedelta | None): The length of the entry.
        link (str): Audio link of the entry.
    """
    def __init__(self, row: Row):
        self.era_name: str = SimpleColumn(row, 0)() #: Test comment

        self.notes = SimpleColumn(row, 2)()
        self.length = TrackLength(row, 3)()
        self.link = SimpleColumn(row, 8)()

        self._set_name_attrs(row)
        self._set_era_attrs(self.era_name)

class Unreleased(Song):
    """Represents an entry in the Unreleased tab.  
    Inherits attributes from the `Song` class.
    
    Attributes:
        file_date (datetime | str | None): The date of the song file itself.
            Either a plain-text string of the date,
            or a `datetime` object if the date is exact.
        leak_date (datetime | str | None): The date of the song's leakage.
            See `file_date` for information about the type.
        available_length (AvailableLengthEnum | None): 
            How much of the song is available.
        quality (QualityEnum | None): The audio quality of the song.
    """
    def __init__(self, row: Row):
        super().__init__(row)

        self.file_date = Date(row, 4)()
        self.leak_date = Date(row, 5)()

        self.available_length = AvailableLength(row, 6)()
        self.quality = Quality(row, 7)()

class Released(Song):
    """Represents an entry in the Released tab.  
    Inherits attributes from the `Song` class.
    
    Attributes:
        release_date (datetime | str | None): The song's release date.
            See `file_date` of `Unreleased` for information about the type.
        type (ReleasedType): The type of the release.
        streaming (bool): Whether the song is streaming or not.
    """
    def __init__(self, row: Row):
        super().__init__(row)

        self.link = SimpleColumn(row, 7)()

        self.release_date = Date(row, 4)()
        self.type = ReleasedType(row, 5)
        self.streaming = Streaming(row, 6)()

class Stem(Song):
    """Represents an entry in the Stems tab.  
    Inherits attributes from the `Song` class.

    Shares the `file_date`, `leak_date`, `available_length`,
    and `quality` attributes with `Unreleased`.
    
    Attributes:
        bpm (str): The BPM of the stems.
    """
    def __init__(self, row: Row):
        super().__init__(row)

        self.link = SimpleColumn(row, 9)()
        self.length = TrackLength(row, 5)()

        self.file_date = Date(row, 3)()
        self.leak_date = Date(row, 4)()
        self.bpm = SimpleColumn(row, 6)()
        self.available_length = AvailableLength(row, 7)()
        self.quality = Quality(row, 8)()

class Sample(Entry, WithNames):
    """Represents an entry in the Samples tab.  
    Inherits attributes from `WithNames`.

    Shares the `era_name`, `notes`, and `links` attributes
    with `Song`.

    Attributes:
        samples (list[SampleUsed]): The samples used by a song.
    """
    def __init__(self, row: Row):
        super().__init__(row)

        self.era_name: str = SimpleColumn(row, 0)()
        self.notes = SimpleColumn(row, 3)()
        self.links = SimpleColumn(row, 4)()

        self.samples = SampleColumn(row, 2)()
        self.samples = SampleColumn.modify_samples_used(
            self.samples, 
            self.notes,
            self.links
        )

        self._set_name_attrs(row)
