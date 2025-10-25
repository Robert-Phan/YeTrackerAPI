# Ye Tracker

This is an unofficial Python API for interacting with the Ye Tracker, a project that catalogues information about the unreleased music of rapper and producer Ye. (May expand to trackers for other artists in the future).

# Usage Guide
## Full documentation

See INSERT LINK to view the project's full documentation.

## Getting a Google Sheets API Key

This project is reliant on the Google Sheets API, and requires an API key to be supplied to work.
See [this link](https://developers.google.com/workspace/sheets/api/quickstart/python) as a starter on how to 
obtain an API key.

## Install and Use

Install the package via `pip`:

```
pip install ye-tracker
```

Below is an example of how to use the module:

```python
# Import the `YeTracker` class
from yetracker import YeTracker

# The spreadsheet ID is the long alphanumeric string after the /d/ in the spreadsheet's URL
SPREADSHEET_ID = "Place your spreadsheet ID here."  

with open('API_KEY', 'r') as file:
    # Get your API key
    api_key = file.read() 

    # Create a tracker object.
    tracker = YeTracker(spreadsheet_id=SPREADSHEET_ID, api_key=api_key)

    # Get the list of unreleased songs
    unreleased = tracker.get_unreleased()

    # Print the first unreleased song
    print(unreleased[0])
```

The printed result should look something like this:

```python
{'alt_names': ['On 10 in a Benz'],
 'artist': None,
 'available_length': <AvailableLengthEnum.FULL: 'Full'>,
 'contribs': {'feat': 'Rhymefest & Kanye West',
 'prod': 'Kanye West & Andy C.',
 'ques': '',
 'ref': '',
 'with_': 'Go Getters'},
 'emojis': [],
 'era': {'alt_names': ['Get Well Soon...', "I'm Good...", 'Kon The Louis Vuitton Don'],
 'events': {'06/08/1977': 'Kanye West is born in Atlanta',
            '08/18/2002': 'Kanye announces he signed to Roc-A-Fella'},
 'main_name': 'Before The College Dropout',
 'notes': 'Before Kanye released his first album to critical acclaim in 2004, '
          'he pursued many other projects, including a rap trio group named '
          'the "Go Getters" and production for other rappers, including, but '
          'not limited to JAY-Z, Common, Talib Kweli, and Scarface. Two years '
          'before the release of The College Dropout, Kanye began releasing a '
          'series of mixtapes to generate hype and publicity for the eventual '
          'release of his first album. Kanye eventually signed with '
          'Roc-A-Fella records in August 2002.',
 'stats': {'Full': 42,
           'OG File(s)': 1,
           'Partial': 2,
           'Snippet(s)': 3,
           'Stem Bounce(s)': 0,
           'Tagged': 1,
           'Unavailable': 68}},
 'era_name': 'Before The College Dropout',
 'file_date': None,
 'full_name': '10 in a Benz \n'
              '(with Go Getters) (feat. Rhymefest & Kanye West) (prod. Kanye '
              'West & Andy C.)\n'
              '(On 10 in a Benz)',
 'leak_date': None,
 'length': datetime.timedelta(seconds=254),
 'link': 'https://pillows.su/f/47bf0495be0f1af721cfb718834c48f3',
 'main_name': '10 in a Benz ',
 'notes': "Track 10 from Go Getters' 1999 compilation tape World Record "
          'Holders.\n'
          "Released on GLC's Soundcloud.",
 'quality': <QualityEnum.HIGH_QUALITY: 'High Quality'>,
 'subera': None,
 'version': None}
 ```