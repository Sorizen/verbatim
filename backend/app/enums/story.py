from enum import StrEnum


class Genre(StrEnum):
    DRAMA = 'drama'
    ROMANCE = 'romance'
    REVENGE = 'revenge'
    THRILLER = 'thriller'
    COMEDY = 'comedy'
    WESTERN = 'western'
    CRIME = 'crime'
    FANTASY = 'fantasy'


class Tone(StrEnum):
    TENSE = 'tense'
    PLAYFUL = 'playful'
    DARK = 'dark'
    WARM = 'warm'
    IRONIC = 'ironic'


class TimeOfDay(StrEnum):
    MORNING = 'morning'
    DAY = 'day'
    EVENING = 'evening'
    NIGHT = 'night'


class AssumptionSource(StrEnum):
    USER = 'user'
    INFERRED = 'inferred'
