from abc import ABC, abstractmethod
from typing import Any
import json
import pprint

from yetracker.era import *
from yetracker.entry import *

class Tab[T: Entry](list[T], ABC):
    "Base class for a tab/sheet within a tracker."

    @property
    @abstractmethod
    def entry_type(self) -> type[T]:
        pass

    def __init__(self, raw_values: Range):
        """
        Args:
            values: The two-dimensional array representing 
                a range of cells, or its JSON.
        """

        super().__init__()
        self.eras = []

        for i, row in enumerate(raw_values):
            # print(i)
            if i == 0:
                continue

            if Era.is_era(row):
                self.eras.append(Era(row))
            elif SubEra.is_subera(row):
                continue
            elif self.is_end(row):
                break
            elif len(row) == 1:
                continue
            else:                
                self.append(
                    self.entry_type(row)
                )

    def is_end(self, row: Row):
        for i, x in enumerate(['Links', '', 'Quality']):
            if x != row[i]:
                return False
        
        return True

class UnreleasedTab(Tab[Unreleased]):
    @property
    def entry_type(self):
        return Unreleased

class ReleasedTab(Tab[Released]):
    @property
    def entry_type(self):
        return Released

class StemsTab(Tab[Stem]):
    @property
    def entry_type(self):
        return Stem

def make_emoji_subtab(*match_emojis: Emoji):
    def inner_dec[T: UnreleasedTab](cls: type[T]):
        super_init = cls.__init__

        def __init__(self: T, raw_values: Range):
            super_init(self, raw_values)
            matched_entries = [
                entry for entry in self 
                if any(emoji in entry.emojis 
                        for emoji in match_emojis)
            ]

            self.clear()
            self += matched_entries

        cls.__init__ = __init__
        return cls
    return inner_dec

@make_emoji_subtab(Emoji.BEST_OF)
class BestOf(UnreleasedTab):
    pass

@make_emoji_subtab(Emoji.WORST_OF)
class WorstOf(UnreleasedTab):
    pass

@make_emoji_subtab(Emoji.SPECIAL)
class Special(UnreleasedTab):
    pass

@make_emoji_subtab(Emoji.GRAIL, Emoji.WANTED)
class GrailsOrWanted(UnreleasedTab):
    pass

@make_emoji_subtab(Emoji.AI)
class AI(UnreleasedTab):
    pass

