from abc import ABC, abstractmethod
from typing import Any, TypeGuard
import json
import pprint

from yetracker.era import *
from yetracker.entry import *

class EraManager:
    def __init__(self, era_cls: type[Era] | None, subera_cls: type[SubEra] | None):
        self._era_cls = era_cls
        self._subera_cls = subera_cls

        self.eras: list[Era] = []
        self.suberas: list[SubEra] = []

        self._current_era: Era | None = None
        self._current_subera: SubEra | None = None

    def manage_era(self, row: Row) -> bool:
        if self._era_cls is not None and self._era_cls.is_era(row):
            era = self._era_cls(row)
            self._current_era = era
            self._current_subera = None
            self.eras.append(era)
        elif self._subera_cls is not None and self._subera_cls.is_subera(row):
            subera = self._subera_cls(row)
            self._current_subera = subera
            self.suberas.append(subera)
        else:
            return False

        return True

    def set_era_and_subera(self, entry: Entry):
        if self._current_era is not None:
            entry.set_era(self._current_era)

        if self._current_subera is not None:
            entry.set_subera(self._current_subera)
        
class Tab[T: Entry](list[T], ABC):
    "Base class for a tab/sheet within a tracker."

    @property
    @abstractmethod
    def entry_cls(self) -> type[T]:
        pass

    @abstractmethod
    def get_era_manager(self) -> EraManager:
        pass
    
    def is_end(self, row: Row) -> bool:
        return False

    def __init__(self, raw_values: Range):
        """
        Args:
            values: The two-dimensional array representing 
                a range of cells, or its JSON.
        """

        super().__init__()
        
        era_manager = self.get_era_manager()

        for i, row in enumerate(raw_values):
            if i == 0 or len(row) == 1:
                continue

            if era_manager.manage_era(row):
                continue
            
            if self.is_end(row):
                break
                        
            entry = self.entry_cls(row)
            era_manager.set_era_and_subera(entry)

            self.append(
                entry
            )

        self.eras = era_manager.eras

class UnreleasedTab(Tab[Unreleased]):
    @property
    def entry_cls(self):
        return Unreleased

    def is_end(self, row: Row):
        for i, x in enumerate(['Links', '', 'Quality']):
            if x != row[i]:
                return False
        
        return True

    def get_era_manager(self) -> EraManager:
        return EraManager(BasicEra, BasicSubEra)

class ReleasedTab(Tab[Released]):
    @property
    def entry_cls(self):
        return Released

    def get_era_manager(self) -> EraManager:
        return EraManager(BasicEra, BasicSubEra)

class StemsTab(Tab[Stem]):
    @property
    def entry_cls(self):
        return Stem

    def get_era_manager(self) -> EraManager:
        return EraManager(BasicEra, StemSubEra)

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

