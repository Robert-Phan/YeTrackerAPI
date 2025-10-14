from abc import ABC, abstractmethod
from googleapiclient.discovery import build

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

class YeTracker(Tracker):
    def __init__(self, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        super().__init__()

    def get_unreleased(self):
        if not self.raw_values_fetcher.api_key_supplied:
            raise APIKeyMissingError()
        
        raw_values = self.raw_values_fetcher.get_raw_values("Unreleased")

        return UnreleasedTab(raw_values)
    
    @property
    def spreadsheet_id(self) -> str:
        return self._spreadsheet_id
    
    @spreadsheet_id.setter
    def spreadsheet_id(self, val: str):
        self._spreadsheet_id = val

