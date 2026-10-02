from enum import StrEnum


class ScriptVerdict(StrEnum):
    PASS = 'pass'
    REVISE = 'revise'


class ScriptIssueKind(StrEnum):
    WEAK_HOOK = 'weak_hook'
    UNCLEAR_CONFLICT = 'unclear_conflict'
    WEAK_ENDING = 'weak_ending'
    LINE_TOO_LONG = 'line_too_long'
    OFF_BRIEF = 'off_brief'


class PortraitVerdict(StrEnum):
    PASS = 'pass'
    REDRAW = 'redraw'


class SceneVerdict(StrEnum):
    PASS = 'pass'
    RETRY = 'retry'
    REBUILD_SHOT = 'rebuild_shot'
    NEEDS_REVIEW = 'needs_review'


class DiffOp(StrEnum):
    SUBSTITUTE = 'sub'
    DELETE = 'del'
    INSERT = 'ins'


class SpeakerVisibility(StrEnum):
    ON_SCREEN = 'on_screen'
    UNSEEN = 'unseen'
    OTHER_CHARACTER = 'other_character'
    LIPS_STILL = 'lips_still'


class PhantomSpeech(StrEnum):
    SOUND_NOTE = 'sound_note'
    KNOWN_PHRASE = 'known_phrase'


class VideoArtifact(StrEnum):
    FACE_MORPH = 'face_morph'
    EXTRA_LIMBS = 'extra_limbs'
    HANDS = 'hands'
    FLICKER = 'flicker'


class ShotFixReason(StrEnum):
    TRUNCATED = 'truncated'
    MUMBLED = 'mumbled'
    OVERLAP = 'overlap'
    WRONG_SPEAKER = 'wrong_speaker'
    ON_SCREEN_TEXT = 'on_screen_text'
