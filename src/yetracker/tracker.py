from abc import ABC, abstractmethod
from googleapiclient.discovery import build
from typing import Callable, TextIO

from yetracker.raw_values import *
from yetracker.tab import *

class NotAuthenticatedError(Exception):
    pass

class Tracker(ABC):
    "Base class for a tracker. Inherit to create a specific tracker."

    @overload
    def __init__(self, *, spreadsheet_id: str, api_key: str):
        """Initializes the tracker with the Google Sheets API.
        
        Arguments:
            spreadsheet_id: The ID of the Google Sheets spreadsheet.
            api_key: The API key used to access the sheet.
        """
        ...

    @overload
    def __init__(self, *, raw_json: str | TextIO):
        """Initializes the tracker using a JSON data source.
        
        Arguments:
            raw_json: Either a JSON string in the format of an API response, 
                or as a file handler to a JSON file of that format.
        """
        ...

    @overload
    def __init__(self):
        """Initializes the tracker with no initial data source.
        Data source will need to be provided later."""
        ...

    def __init__(self, *, 
                 spreadsheet_id: str | None = None, 
                 api_key: str | None = None, 
                 raw_json: str | TextIO | None = None
        ):
        
        self.collected_raw_values: list[RawTabDict] = []

        if spreadsheet_id is not None and api_key is not None:
            self.use_api(spreadsheet_id, api_key)
        elif raw_json is not None:
            self.use_json(raw_json)

    def use_json(self, json: str | TextIO):
        """Set the tracker to use a JSON data source.
        
        Arguments:
            json: Either a JSON string in the format of an API response, 
                or as a file handler to a JSON file of that format.
        """
        self.raw_values_fetcher = RawValuesFromJson(json)
        
    def use_api(self, spreadsheet_id: str, api_key: str):
        """Set the tracker to use the Google Sheets API.
        
        Arguments:
            spreadsheet_id: The ID of the Google Sheets spreadsheet.
            api_key: The API key used to access the sheet.
        """
        self.raw_values_fetcher = RawValuesFromAPI(spreadsheet_id)
        self.raw_values_fetcher.authenticate(api_key)
    
    def save_data_to_file(self, file_name: str):
        """Save the raw data collected to a file.  
        The file can subsequently be loaded in with `use_json`.
        
        Arguments:
            file_name: name of the file to be written to.
        """
        with open(file_name, 'w') as f:
            json.dump(self.collected_raw_values, f)
    
    def _get_general[T: Tab](self, sheet_name: str, tab_cls: type[T]) -> T:
        if not self.raw_values_fetcher.authenticated:
            raise NotAuthenticatedError()

        raw_values: Range = self.raw_values_fetcher.get_raw_values(sheet_name)

        raw_tab_dict: RawTabDict = {
            'range': sheet_name,
            'values': raw_values
        }
        self.collected_raw_values.append(raw_tab_dict)

        return tab_cls(raw_values)

class YeTracker(Tracker):
    """Class representing the Ye Tracker."""

    def get_unreleased(self):
        return self._get_general("Unreleased", UnreleasedTab)
    
    def get_released(self):
        return self._get_general("Released", ReleasedTab)

    def get_stems(self):
        return self._get_general("Stems", StemsTab)
    
    def get_samples(self):
        return self._get_general("Samples", SamplesTab)
