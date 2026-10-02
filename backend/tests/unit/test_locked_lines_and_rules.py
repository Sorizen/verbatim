import pytest

from app.enums import AssumptionSource, Genre, ScriptIssueKind, TimeOfDay, Tone
from app.exceptions import LockedLineTooLongError
from app.pipeline.contracts import Assumption, Brief, BriefCharacter, BriefSetting, Line, Script, Shot
from app.pipeline.rules import check_script_rules, ensure_locked_lines_fit, extract_locked_lines

LOCKED_LINE = 'Nice hat, big man. Did your mother pick it out?'


def make_brief(locked_lines: list[str]) -> Brief:
    return Brief(
        logline='A provocation in a saloon',
        genre=Genre.WESTERN,
        tone=Tone.TENSE,
        setting=BriefSetting(place='saloon', time_of_day=TimeOfDay.NIGHT, era='1880s'),
        characters=[
            BriefCharacter(id='c1', name='Jake', role='provoker', age=34),
            BriefCharacter(id='c2', name='Tom', role='provoked', age=41),
        ],
        target_duration_s=15,
        assumptions=[Assumption(field='era', value='1880s', source=AssumptionSource.INFERRED)],
        locked_lines=locked_lines,
    )


def make_script(*shots: Shot) -> Script:
    return Script(title='The hat', shots=list(shots))


def test_extracts_straight_and_curly_quotes_exactly() -> None:
    idea = f'He says "{LOCKED_LINE}" and the other replies “Get out.”'
    assert extract_locked_lines(idea) == [LOCKED_LINE, 'Get out.']


def test_rejects_quoted_line_that_cannot_fit_a_shot() -> None:
    with pytest.raises(LockedLineTooLongError):
        ensure_locked_lines_fit([' '.join(['word'] * 60)])


def test_valid_script_has_no_violations() -> None:
    script = make_script(
        Shot(id='s1', beat='mock', duration_s=5, line=Line(speaker='c1', text=LOCKED_LINE, emotion='x', locked=True)),
        Shot(id='s2', beat='reply', duration_s=5, line=Line(speaker='c2', text='Get out.', emotion='x', locked=False)),
    )
    assert check_script_rules(script, make_brief([LOCKED_LINE])) == []


def test_flags_fast_pace_unknown_speaker_and_missing_locked_line() -> None:
    rushed = Line(speaker='c3', text='one two three four five six seven eight nine ten', emotion='x', locked=False)
    script = make_script(
        Shot(id='s1', beat='rushed', duration_s=2, line=rushed),
        Shot(id='s2', beat='pause', duration_s=6, line=None),
    )
    kinds = [violation.kind for violation in check_script_rules(script, make_brief([LOCKED_LINE]))]
    assert ScriptIssueKind.LINE_TOO_LONG in kinds
    assert kinds.count(ScriptIssueKind.OFF_BRIEF) == 2
