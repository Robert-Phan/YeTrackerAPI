from abc import ABC, abstractmethod
from typing import Any, TypeGuard
import json
import pprint

from yetracker.common import *
from yetracker.era import *
from yetracker.entry import *

class _EraManager:
    def __init__(self, 
                 era_cls: type[Era] = BasicEra, 
                 subera_cls: type[SubEra] = BasicSubEra,
                 no_eras: bool = False):
        self.no_eras = no_eras

        self._era_cls = era_cls
        self._subera_cls = subera_cls

        self.eras: list[Era] = []
        self.suberas: list[SubEra] = []

        self._current_era: Era | None = None
        self._current_subera: SubEra | None = None

    def manage_era(self, row: Row) -> bool:
        if self.no_eras:
            return False

        if self._era_cls._is_era(row):
            era = self._era_cls(row)
            self._current_era = era
            self._current_subera = None
            self.eras.append(era)
        elif self._subera_cls._is_subera(row):
            subera = self._subera_cls(row)
            self._current_subera = subera
            self.suberas.append(subera)
        else:
            return False

        return True

    def set_era_and_subera(self, entry: WithEras):
        if self._current_era is not None:
            entry.set_era(self._current_era)

        if self._current_subera is not None:
            entry.set_subera(self._current_subera)
        
class Tab[T: Entry](list[T], ABC):
    "Base class for a tab/sheet within a tracker."

    @property
    @abstractmethod
    def _entry_cls(self) -> type[T]:
        pass

    @abstractmethod
    def _get_era_manager(self) -> _EraManager:
        pass

    def _ignore_row(self, row_idx: int, row: Row) -> bool:
        return row_idx == 0 or len(row) == 1 or row[0] == ''
    
    def _is_end(self, row: Row) -> bool:
        return False

    def __init__(self, raw_values: Range):
        """
        Args:
            values: The two-dimensional array representing 
                a range of cells, or its JSON.
        """

        super().__init__()
        
        era_manager = self._get_era_manager()

        for i, row in enumerate(raw_values):
            if self._ignore_row(i, row):
                continue

            if era_manager.manage_era(row):
                continue
            
            if self._is_end(row):
                break
            
            entry = self._entry_cls(row)

            if isinstance(entry, WithEras):
                era_manager.set_era_and_subera(entry)

            self.append(entry)

        self.eras = era_manager.eras

class UnreleasedTab(Tab[Unreleased]):
    """List of entries in the Unreleased tab."""
    @property
    def _entry_cls(self):
        return Unreleased

    def _is_end(self, row: Row):
        for i, x in enumerate(['Links', '', 'Quality']):
            if x != row[i]:
                return False
        
        return True

    def _get_era_manager(self) -> _EraManager:
        return _EraManager()

    def _get_emoji_subtab(self, *match_emojis: Emoji) -> 'UnreleasedTab':
        new_tab = UnreleasedTab([])
        new_tab.eras = self.eras

        for entry in self:
            if any(match_emoji in entry.emojis 
                   for match_emoji in match_emojis):
                new_tab.append(entry)
            
        return new_tab

    def get_best_of(self):
        """Returns a filtered `UnreleasedTab` with only 
        entries that have the "Best Of" emoji."""
        return self._get_emoji_subtab(Emoji.BEST_OF)
    
    def get_worst_of(self):
        """Returns a filtered `UnreleasedTab` with only 
        entries that have the "Worst Of" emoji."""
        return self._get_emoji_subtab(Emoji.WORST_OF)
    
    def get_ai(self):
        """Returns a filtered `UnreleasedTab` with only 
        entries that have the "AI" emoji."""
        return self._get_emoji_subtab(Emoji.AI)
    
    def get_special(self):
        """Returns a filtered `UnreleasedTab` with only 
        entries that have the "Special" emoji."""

        return self._get_emoji_subtab(Emoji.SPECIAL)
    
    def get_grails_or_wanted(self):
        """Returns a filtered `UnreleasedTab` with only 
        entries that either have the "Grail" or the "Wanted" emoji."""
        return self._get_emoji_subtab(Emoji.GRAIL, Emoji.WANTED)

class ReleasedTab(Tab[Released]):
    """List of entries in the Released tab."""
    @property
    def _entry_cls(self):
        return Released

    def _get_era_manager(self) -> _EraManager:
        return _EraManager()

class StemsTab(Tab[Stem]):
    """List of entries in the Stems tab."""
    @property
    def _entry_cls(self):
        return Stem

    def _get_era_manager(self) -> _EraManager:
        return _EraManager(subera_cls=StemSubEra)

class SamplesTab(Tab[Sample]):
    """List of entries in the Samples tab."""
    @property
    def _entry_cls(self):
        return Sample

    def _get_era_manager(self) -> _EraManager:
        return _EraManager(no_eras=True)

