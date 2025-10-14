from abc import ABC, abstractmethod
from typing import Any
import json
import pprint

from yetracker.column import * 
from yetracker.era import *

class Tab(list, ABC):
    "Base class for a tab/sheet within a tracker"

    @abstractmethod
    def __init__(self, raw_values: Range):
        """
        Args:
            values: The two-dimensional array representing 
                a range of cells, or its JSON.
        """

        super().__init__()
        self._raw_values = raw_values
        self.eras = []
    
class Unreleased:
    def __init__(self, row: Row):
        self.era = SimpleColumn(row, 0)()
        self.notes = SimpleColumn(row, 2)()
        self.link = SimpleColumn(row, 8)()

        self.track_length = TrackLength(row, 3)()
        self.file_date = Date(row, 4)()
        self.leak_date = Date(row, 5)()

        self.available_length = AvailableLength(row, 6)()
        self.quality = Quality(row, 7)()

        name_column = Name(row, 1)
        self.full_name = name_column()
        self.main_name = name_column.main_name
        self.emojis = name_column.emojis
        self.version = name_column.version
        self.contribs = name_column.contribs
        self.alt_names = name_column.alt_names
    
    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

class UnreleasedTab(Tab):
    def is_end(self, row: Row):
        for i, x in enumerate(['Links', '', 'Quality']):
            if x != row[i]:
                return False
        
        return True

    def __init__(self, raw_values: Range):
        super().__init__(raw_values)

        for i, row in enumerate(self._raw_values):
            print(i)
            if i == 7343:
                print(row)

            if Era.is_era(row):
                self.eras.append(Era(row))
            elif SubEra.is_subera(row):
                continue
            elif self.is_end(row):
                break
            else:
                self.append(
                    Unreleased(row)
                )
