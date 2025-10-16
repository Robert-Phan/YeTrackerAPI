from abc import ABC, abstractmethod
import pprint

from yetracker.column import * 
from yetracker.era import *
from yetracker.era import Era

class Entry(ABC):
    @abstractmethod
    def __init__(self, row: Row):
        pass
    
    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)\
    
    @abstractmethod
    def set_era(self, era: Era):
        pass

    @abstractmethod
    def set_subera(self, subera: SubEra):
        pass

class Song(Entry):
    def __init__(self, row: Row):
        self.era: str | Era = SimpleColumn(row, 0)()
        self.subera: SubEra | None = None

        self.notes = SimpleColumn(row, 2)()
        self.length = TrackLength(row, 3)()
        self.link = SimpleColumn(row, 8)()

        name_column = Name(row, 1)
        self.full_name = name_column()
        self.main_name = name_column.main_name
        self.emojis = name_column.emojis
        self.version = name_column.version
        self.contribs = name_column.contribs
        self.alt_names = name_column.alt_names

    def set_era(self, era: Era):
        self.era = era

    def set_subera(self, subera: SubEra):
        self.subera = subera

class Unreleased(Song):
    def __init__(self, row: Row):
        super().__init__(row)

        self.file_date = Date(row, 4)()
        self.leak_date = Date(row, 5)()

        self.available_length = AvailableLength(row, 6)()
        self.quality = Quality(row, 7)()

class Released(Song):
    def __init__(self, row: Row):
        super().__init__(row)

        self.link = SimpleColumn(row, 7)()

        self.release_date = Date(row, 4)()
        self.type = ReleasedType(row, 5)
        self.streaming = Streaming(row, 6)()

class Stem(Song):
    def __init__(self, row: Row):
        super().__init__(row)

        self.link = SimpleColumn(row, 9)()
        self.length = TrackLength(row, 5)()

        self.file_date = Date(row, 3)()
        self.leak_date = Date(row, 4)()
        self.bpm = SimpleColumn(row, 6)
        self.available_length = AvailableLength(row, 7)()
        self.quality = Quality(row, 8)()
