import pytest

from app.enums import PhantomSpeech, SceneVerdict, SpeakerVisibility
from app.pipeline.checks import decide_scene_verdict, drop_phantom_speech
from app.pipeline.checks.judge_windows import apply_speaker_verdicts
from app.pipeline.contracts import FormatCheck, LineCheck, SceneJudgment, SpeakerVerdict
from app.providers.types import Transcript, TranscriptSegment, TranscriptWord

GOOD_FORMAT = FormatCheck(aspect_ok=True, duration_s=15.0, duration_ok=True, has_audio=True)
LINE_WORDS = ['nice', 'hat', 'big', 'man']


def word(text: str, start: float, end: float) -> TranscriptWord:
    return TranscriptWord(word=text, start=start, end=end)


def test_sound_notes_and_known_phrases_are_dropped() -> None:
    transcript = Transcript(
        text=' *Drum roll* Nice hat, big man. Thank you.',
        cost_usd=0.0,
        segments=[
            TranscriptSegment(text=' *Drum roll*', start=0.0, end=1.54),
            TranscriptSegment(text=' Nice hat, big man.', start=1.86, end=3.86),
            TranscriptSegment(text=' Thank you.', start=6.0, end=6.6),
        ],
        words=[
            word(' *Drum', 0.0, 0.4),
            word(' roll', 0.4, 0.48),
            word('*', 0.48, 0.48),
            word(' Nice', 1.86, 2.54),
            word(' hat,', 2.54, 2.94),
            word(' big', 2.94, 3.08),
            word(' man.', 3.08, 3.48),
            word(' Thank', 6.0, 6.58),
            word(' you.', 6.58, 6.58),
        ],
    )
    cleaned, ignored = drop_phantom_speech(transcript, LINE_WORDS)
    assert [item.word.strip() for item in cleaned.words] == ['Nice', 'hat,', 'big', 'man.']
    assert [item.reason for item in ignored] == [PhantomSpeech.SOUND_NOTE, PhantomSpeech.KNOWN_PHRASE]


def test_a_known_phrase_that_belongs_to_the_line_is_kept() -> None:
    transcript = Transcript(
        text=' Thank you.',
        cost_usd=0.0,
        segments=[TranscriptSegment(text=' Thank you.', start=0.0, end=0.6)],
        words=[word(' Thank', 0.0, 0.3), word(' you.', 0.3, 0.6)],
    )
    cleaned, ignored = drop_phantom_speech(transcript, ['thank', 'you', 'sir'])
    assert ignored == []
    assert len(cleaned.words) == 2


@pytest.mark.parametrize(
    ('visibility', 'passes'),
    [
        (SpeakerVisibility.ON_SCREEN, True),
        (SpeakerVisibility.UNSEEN, True),
        (SpeakerVisibility.OTHER_CHARACTER, False),
        (SpeakerVisibility.LIPS_STILL, False),
    ],
)
def test_only_another_or_a_still_mouth_fails_the_speaker(visibility: SpeakerVisibility, passes: bool) -> None:
    line = LineCheck(
        shot_id='s1',
        speaker='c1',
        expected='Nice hat, big man.',
        heard='nice hat big man',
        wer=0.0,
        diff=[],
        alignment=[],
        start_s=1.8,
        end_s=3.5,
        speaker_matches=None,
    )
    judgment = SceneJudgment(
        physics_integrity=9,
        temporal_continuity=9,
        reaction_plausibility=9,
        character_presence_consistency=10,
        on_screen_text=False,
        artifacts=[],
        speakers=[SpeakerVerdict(shot_id='s1', visibility=visibility)],
        analysis='',
    )
    judged = apply_speaker_verdicts([line], judgment)
    verdict, _ = decide_scene_verdict(attempt=1, format_check=GOOD_FORMAT, lines=judged, judgment=judgment)
    assert judged[0].speaker_matches is passes
    assert (verdict == SceneVerdict.PASS) is passes
