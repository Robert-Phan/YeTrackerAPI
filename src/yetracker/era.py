import re
import pprint
from typing import Protocol

from yetracker.column import *

"""Test."""

@add_repr
class Era(ABC):
    @abstractmethod
    def __init__(self, row: Row) -> None:
        pass

    @classmethod
    @abstractmethod
    def is_era(cls, row: Row) -> bool:
        pass

class BasicEra(Era):
    """Represents a standard era.
    
    Attributes:
        notes (str): Notes about the era.
        stats (dict[str, int]): Statistics about the entries within the era.
        events (dict[str, str]): The events within an era, mapped to the date they happened.
        main_name (str): The main name of the era.
        alt_names (str): Alternative names the era is known by.
    """
    def __init__(self, row: Row):
        self.notes = SimpleColumn(row, 5)()

        self.stats = EraStats(row, 0)()
        self.events = EraEvents(row, 2)()

        name = EraName(row, 1)
        self.main_name = name()
        self.alt_names = name.alt_names

    @classmethod
    def is_era(cls, row: Row):
        return len(row) == 6

@add_repr
class SubEra(ABC):
    @abstractmethod
    def __init__(self, row: Row) -> None:
        pass

    @classmethod
    @abstractmethod
    def is_subera(cls, row: Row) -> bool:
        pass

class BasicSubEra(SubEra):
    """Represents a standard subera.
    
    Attributes:
        events (dict[str, str]): The events within an era with the date they happened.
        name (str): The subera's name.
    """
    def __init__(self, row: Row):
        self.name = SimpleColumn(row, 1)()
        self.events = EraEvents(row, 2)()

    @classmethod
    def is_subera(cls, row: Row):
        return len(row) == 3
    
class StemSubEra(SubEra):
    """Represents a subera within the `Stems` tab.

    Attributes:
        stem_type (StemTypeEnum | None): The type of the stem.
    """
    def __init__(self, row):
        self.stem_type = StemType(row, 1)()

    @classmethod
    def is_subera(cls, row: Row):
        return len(row) == 2

class MusicVideosSubEra(SubEra):
    def __init__(self, row: Row):
        self.release_status = MVStatus(row, 1)()

    @classmethod
    def is_subera(cls, row: Row):
        return len(row) == 2
