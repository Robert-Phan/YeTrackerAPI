from abc import ABC, abstractmethod
from googleapiclient.discovery import build
import json

type Row = list[str]
type Range = list[Row]

class RawValuesFetcher(ABC):
    @abstractmethod
    def get_raw_values(self, tab_name: str) -> Range:
        pass

class RawValuesFromAPI(RawValuesFetcher):
    def __init__(self, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        self.api_key_supplied = False

    def use_api_key(self, api_key: str):
        service = build('sheets', 'v4', developerKey=api_key)
        self.spreadsheets = service.spreadsheets()
        self.values = self.spreadsheets.values()
        self.api_key_supplied = True
        return self
    
    def get_raw_values(self, tab_name: str) -> Range:
        response = self.values.get(
            spreadsheetId=self.spreadsheet_id,
            range=tab_name
        ).execute()

        return response['values']
