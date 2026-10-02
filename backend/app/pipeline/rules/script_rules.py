from collections import Counter

from app.constants import MAX_OWN_LINE_WORDS, MAX_SCENE_SECONDS, MAX_WORDS_PER_SECOND, MIN_SCENE_SECONDS
from app.enums import ScriptIssueKind
from app.pipeline.checks.text import count_words
from app.pipeline.contracts import Brief, RuleViolation, Script, Shot

SCENE_LENGTH_TEMPLATE = 'the scene lasts {seconds} s, it must last {low}-{high} s'
OWN_LINE_TEMPLATE = 'the line has {words} words, own lines are limited to {limit}'
PACE_TEMPLATE = 'the line needs at least {needed:.1f} s at {pace} words per second, the shot lasts {seconds} s'
SPEAKER_TEMPLATE = 'speaker {speaker} is not a character of the brief'
LOCKED_MISSING_TEMPLATE = 'locked line {index} is not used'
LOCKED_REPEATED_TEMPLATE = 'locked line {index} is used {times} times'
SHOT_IDS_TEMPLATE = 'shot ids must be s1..s{count} in order'
SHOT_ID_PREFIX = 's'


def check_scene_length(script: Script) -> list[RuleViolation]:
    seconds = script.total_seconds
    if MIN_SCENE_SECONDS <= seconds <= MAX_SCENE_SECONDS:
        return []
    detail = SCENE_LENGTH_TEMPLATE.format(seconds=seconds, low=MIN_SCENE_SECONDS, high=MAX_SCENE_SECONDS)
    return [RuleViolation(kind=ScriptIssueKind.OFF_BRIEF, shot_id=None, detail=detail)]


def check_shot_ids(script: Script) -> list[RuleViolation]:
    expected = [f'{SHOT_ID_PREFIX}{number}' for number in range(1, len(script.shots) + 1)]
    if [shot.id for shot in script.shots] == expected:
        return []
    detail = SHOT_IDS_TEMPLATE.format(count=len(script.shots))
    return [RuleViolation(kind=ScriptIssueKind.OFF_BRIEF, shot_id=None, detail=detail)]


def check_shot_line(shot: Shot, character_ids: set[str]) -> list[RuleViolation]:
    if not shot.line:
        return []
    violations = []
    words = count_words(shot.line.text)
    if not shot.line.locked and words > MAX_OWN_LINE_WORDS:
        detail = OWN_LINE_TEMPLATE.format(words=words, limit=MAX_OWN_LINE_WORDS)
        violations.append(RuleViolation(kind=ScriptIssueKind.LINE_TOO_LONG, shot_id=shot.id, detail=detail))
    needed_seconds = words / MAX_WORDS_PER_SECOND
    if needed_seconds > shot.duration_s:
        detail = PACE_TEMPLATE.format(needed=needed_seconds, pace=MAX_WORDS_PER_SECOND, seconds=shot.duration_s)
        violations.append(RuleViolation(kind=ScriptIssueKind.LINE_TOO_LONG, shot_id=shot.id, detail=detail))
    if shot.line.speaker not in character_ids:
        detail = SPEAKER_TEMPLATE.format(speaker=shot.line.speaker)
        violations.append(RuleViolation(kind=ScriptIssueKind.OFF_BRIEF, shot_id=shot.id, detail=detail))
    return violations


def check_locked_lines(script: Script, brief: Brief) -> list[RuleViolation]:
    used = Counter(shot.line.text for shot in script.shots if shot.line and shot.line.locked)
    violations = []
    for index, text in enumerate(brief.locked_lines):
        times = used[text]
        if not times:
            detail = LOCKED_MISSING_TEMPLATE.format(index=index)
            violations.append(RuleViolation(kind=ScriptIssueKind.OFF_BRIEF, shot_id=None, detail=detail))
        if times > 1:
            detail = LOCKED_REPEATED_TEMPLATE.format(index=index, times=times)
            violations.append(RuleViolation(kind=ScriptIssueKind.OFF_BRIEF, shot_id=None, detail=detail))
    return violations


def check_script_rules(script: Script, brief: Brief) -> list[RuleViolation]:
    character_ids = {character.id for character in brief.characters}
    shot_violations = [violation for shot in script.shots for violation in check_shot_line(shot, character_ids)]
    return [
        *check_scene_length(script),
        *check_shot_ids(script),
        *shot_violations,
        *check_locked_lines(script, brief),
    ]
