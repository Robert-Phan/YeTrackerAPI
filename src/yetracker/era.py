import re
import pprint

from yetracker.column import *

class Era:
    def __init__(self, row: Row):
        self.notes = SimpleColumn(row, 5)()

        self.stats = EraStats(row, 0)()
        self.events = EraEvents(row, 2)()

        name = EraName(row, 1)
        self.main_name = name()
        self.alt_names = name.alt_names

    @staticmethod
    def is_era(row: Row):
        return len(row) == 6
    
    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)


class SubEra:
    @staticmethod
    def is_subera(row: Row):
        return len(row) == 3