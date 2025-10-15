from abc import ABC, abstractmethod
from googleapiclient.discovery import build
from typing import Callable

from yetracker.raw_values import RawValuesFromAPI
from yetracker.tab import *

class APIKeyMissingError(Exception):
    pass

class Tracker(ABC):
    "Base class for a tracker. Inherit to create a specific tracker."

    @abstractmethod
    def __init__(self):
        self.raw_values_fetcher = RawValuesFromAPI(self.spreadsheet_id)
    
    @property
    @abstractmethod
    def spreadsheet_id(self) -> str:
        pass
    
    def use_api_key(self, api_key: str):
        self.raw_values_fetcher.use_api_key(api_key)
        return self
    
    def get_general[T: Tab](self, sheet_name: str, tab_cls: type[T]):
        if not self.raw_values_fetcher.api_key_supplied:
            raise APIKeyMissingError()

        raw_values = self.raw_values_fetcher.get_raw_values(sheet_name)

        return tab_cls(raw_values)

class YeTracker(Tracker):
    def __init__(self, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        super().__init__()

    def get_unreleased(self):
        return self.get_general("Unreleased", UnreleasedTab)
    
    def get_released(self):
        return self.get_general("Released", ReleasedTab)

    def get_stems(self):
        return self.get_general("Stems", StemsTab)
    
    def get_best_of(self):
        return self.get_general("Unreleased", BestOf)
    
    def get_worst_of(self):
        return self.get_general("Unreleased", WorstOf)
    
    def get_special(self):
        return self.get_general("Unreleased", Special)
    
    def get_grails_or_wanted(self):
        return self.get_general("Unreleased", GrailsOrWanted)
    
    def get_ai(self):
        return self.get_general("Unreleased", AI)

    @property
    def spreadsheet_id(self) -> str:
        return self._spreadsheet_id
    
    @spreadsheet_id.setter
    def spreadsheet_id(self, val: str):
        self._spreadsheet_id = val
