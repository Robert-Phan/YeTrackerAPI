from abc import ABC, abstractmethod
from typing import Any, override, Self, overload, Never, Literal
import pprint
import datetime
import re
from enum import Enum, StrEnum

type Row = list[str]
type Range = list[Row]

class Column(ABC):
    def __init__(self, row: Row, column_num: int):
        try:
            self.base_str = row[column_num]
        except:
            self.base_str = ""
    
    @abstractmethod
    def __call__(self) -> object:
        pass

class SimpleColumn(Column):
    def __call__(self) -> str:
        return self.base_str

class TrackLength(Column):
    def __call__(self):
        regex_match = re.search(r'(\d{1,2}):(\d{2})', self.base_str)

        if regex_match is None:
            return None

        minutes = int(regex_match.group(1))
        seconds = int(regex_match.group(2))
        duration = minutes * 60 + seconds
        
        return datetime.timedelta(seconds=duration)
    
class Date(Column):
    def parse_date_str(self, date_str: str) -> datetime.datetime | str | None:
        months = ['Jan', 'Feb', 'Mar', 'Apr',
                  'May', 'Jun', 'Jul', 'Aug'
                  'Sep', 'Oct', 'Nov', 'Dec']
        
        regex_match = re.search(r'(\w{3}) (\d{2}), (\d{4})', date_str)

        if regex_match is None:
            return None
        
        try:
            month = months.index(regex_match.group(1))
            day = int(regex_match.group(2))
            year = int(regex_match.group(3))

            return datetime.datetime(year=year, month=month, day=day)
        except:
            return date_str
        
    def __call__(self):
        return self.parse_date_str(self.base_str)

class Category(Column, ABC):
    @property
    @abstractmethod
    def category_cls(self) -> type[Enum]:
        pass

    def __call__(self) -> Enum | None:
        try:
            return self.category_cls(self.base_str)
        except ValueError:
            return

class AvailableLengthEnum(StrEnum):
    SNIPPET = 'Snippet'
    PARTIAL = 'Partial'
    BEAT_ONLY = 'Beat Only'
    TAGGED = 'Tagged'
    STEM_BOUNCE = 'Stem Bounce'
    FULL = 'Full'
    OG_FILE = 'OG File'
    CONFIRMED = 'Confirmed'
    RUMORED = 'Rumored'
    CONFLICTING_SOURCES = 'Conflicting Sources'

class AvailableLength(Category):
    @property
    def category_cls(self):
        return AvailableLengthEnum

class QualityEnum(StrEnum):
    NOT_AVAILABLE = 'Not Available'
    RECORDING = 'Recording'
    LOW_QUALITY = 'Low Quality'
    HIGH_QUALITY = 'High Quality'
    CD_QUALITY = 'CD Quality'
    LOSSLESS = 'Lossless'

class Quality(Category):
    @property
    def category_cls(self):
        return QualityEnum

class Emoji(Enum):
    BEST_OF = "⭐"
    SPECIAL = "✨"
    GRAIL = "🏆"
    WANTED = "🥇"
    WORST_OF = "🗑️"
    AI = "🤖"
    LOST = "⁉️"

class Version:
    def __init__(self, version_start: int, version_end: int | Literal['?'] | None = None):
        self.version_start = version_start
        self.version_end = version_end

        self.multiple_versions = version_end != None
        if self.multiple_versions:
            self.version = self.version_start

        self.version_count_unknown = version_end == '?'

    @classmethod
    def extract_version(cls, name_str: str) -> tuple[Self | None, str]:
        pattern = r'\[V(\d+)(-V(\d+|\?))*\]'

        regex_match = re.search(pattern, name_str)
        if regex_match is None:
            return None, name_str

        version_start = int(regex_match.group(1))
        version_end = str(regex_match.group(3))

        if version_end == '?':
            pass
        elif version_end == '' or version_end == 'None':
            version_end = None
        else:
            version_end = int(version_end)
        
        name_str = re.sub(pattern, '', name_str)

        return cls(version_start, version_end), name_str

class ContribTag(Enum):
    FEAT = "feat."
    REF  = "ref."
    WITH = "with"
    PROD = "prod."
    QUES = "???."

class Contributors:
    def __init__(self, name_str: str):
        self.feat: str | None = None
        self.ref: str | None = None
        self.with_: str | None = None
        self.prod: str | None = None
        self.ques: str | None = None

        line, name_str = self.get_contrib_line(name_str)
        self._after_parsing = name_str
        if line is None:
            return
        
        self.parse_contrib(line)

    def __repr__(self) -> str:
        print_dict = dict(self.__dict__)
        print_dict.pop('_after_parsing')
        return pprint.pformat(print_dict)
    
    def __call__(self):
        return self._after_parsing

    def parse_contrib(self, line: str):
        words = line.split()

        contrib_word_dict: dict[ContribTag, list[str]] = {
            tag: [] for tag in ContribTag
        }

        mode: ContribTag | None = None

        def add_to_dict(word: str):
            if mode is None:
                return

            contrib_word_dict[mode].append(word)
        
        for word in words:
            if word[0] == '(':
                try:
                    mode = ContribTag(word[1:])
                except:
                    mode = None
            elif word[-1] == ')':
                add_to_dict(word[:-1])
                mode = None
            else:
                add_to_dict(word)
        
        self.feat = ' '.join(contrib_word_dict[ContribTag.FEAT])
        self.ref = ' '.join(contrib_word_dict[ContribTag.REF])
        self.with_ = ' '.join(contrib_word_dict[ContribTag.WITH])
        self.prod = ' '.join(contrib_word_dict[ContribTag.PROD])
        self.ques = ' '.join(contrib_word_dict[ContribTag.QUES])
    
    def get_contrib_line(self, name_str: str) -> tuple[str | None, str]:
        split_by_line = name_str.splitlines()

        if len(split_by_line) == 3:
            name_str = f'{split_by_line[0]}\n{split_by_line[2]}'
            return split_by_line[1], name_str
        elif len(split_by_line) == 2:
            first_word = split_by_line[1].split()[0]
            for tag in ContribTag:
                if first_word == f'({tag}':
                    name_str = split_by_line[0]
                    return split_by_line[1], name_str
        
        return None, name_str

class Name(Column):
    def __call__(self):
        self.emojis, name_str = self.extract_emojis(self.base_str)
        self.version, name_str = self.extract_version(name_str)
        self.contribs, name_str = self.extract_contribs(name_str)
        self.alt_names, name_str = self.extract_alt_names(name_str)
        self.main_name = name_str

        return self.base_str
    
    def extract_emojis(self, name_str: str) -> tuple[list[Emoji], str]:
        emojis: list[Emoji] = []

        for emoji in Emoji:
            emoji_match = re.match(emoji.value, name_str)
            if emoji_match is None:
                continue

            emojis.append(emoji)
            name_str = re.sub(emoji.value, "", name_str)
        
        return emojis, name_str
    
    def extract_version(self, name_str: str) -> tuple[Version | None, str]:        
        return Version.extract_version(name_str)
    
    def extract_contribs(self, name_str: str) -> tuple[Contributors, str]:
        contribs = Contributors(name_str)
        return contribs, contribs()

    def extract_alt_names(self, name_str: str) -> tuple[list[str], str]:
        split_by_line = name_str.splitlines()
        if len(split_by_line) == 1:
            return [], name_str
        else:
            line = split_by_line[1]
            line = line.strip('(').strip(')')
            alt_names = line.split(', ')
            return alt_names, split_by_line[0]

class EraStats(Column):
    def __call__(self) -> dict[str, int]:
        stats: dict[str, int] = {}

        lines = self.base_str.splitlines()
        for line in lines:
            regex_match = re.match(r'(\d+) (.+)', line)
            if regex_match is None:
                continue
            
            count = int(regex_match.group(1))
            status = str(regex_match.group(2))
            stats[status] = count
        
        return stats

class EraName(Column):
    def __call__(self) -> str:
        lines = self.base_str.splitlines()

        self.alt_names: list[str] | None = None
        if len(lines) >= 2:
            alt_names_line = lines[1]
            alt_names_line = alt_names_line.strip('(').strip(')')
            self.alt_names = alt_names_line.split(', ')

        return lines[0]
    
class EraEvents(Column):
    def __call__(self) -> dict[datetime.datetime, str]:
        events: dict[datetime.datetime, str] = {}

        event_lines = self.base_str.splitlines()
        pattern = r'\((\d+\/\d+\/\d+)\) \((.+)\)'

        for line in event_lines:
            regex_match = re.search(pattern, line)
            if regex_match is None:
                continue

            date_str = regex_match.group(1)
            date = datetime.datetime.strptime(date_str, '%m/%d/%Y')
            event = regex_match.group(2)

            events[date] = event
        
        return events