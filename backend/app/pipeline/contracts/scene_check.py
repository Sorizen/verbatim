from pydantic import Field

from app.constants import JUDGE_MAX_SCORE, JUDGE_MIN_SCORE
from app.enums import DiffOp, PhantomSpeech, SceneVerdict, SpeakerVisibility, VideoArtifact
from app.pipeline.contracts.base import Contract


class FormatCheck(Contract):
    aspect_ok: bool
    duration_s: float
    duration_ok: bool
    has_audio: bool


class WordDiff(Contract):
    op: DiffOp
    expected: str | None
    heard: str | None


class AlignedWord(Contract):
    op: DiffOp | None
    expected: str | None
    heard: str | None


class LineCheck(Contract):
    shot_id: str
    speaker: str
    expected: str
    heard: str
    wer: float
    diff: list[WordDiff]
    alignment: list[AlignedWord]
    start_s: float | None
    end_s: float | None
    speaker_matches: bool | None
    speaker_visibility: SpeakerVisibility | None = None


class SpeakerVerdict(Contract):
    shot_id: str
    visibility: SpeakerVisibility = Field(description='How the expected character delivers the line in this window')


class IgnoredSpeech(Contract):
    text: str
    start_s: float
    end_s: float
    reason: PhantomSpeech


class SceneJudgment(Contract):
    physics_integrity: int = Field(ge=JUDGE_MIN_SCORE, le=JUDGE_MAX_SCORE)
    temporal_continuity: int = Field(ge=JUDGE_MIN_SCORE, le=JUDGE_MAX_SCORE)
    reaction_plausibility: int = Field(ge=JUDGE_MIN_SCORE, le=JUDGE_MAX_SCORE)
    character_presence_consistency: int = Field(description='Either 0 or 10')
    on_screen_text: bool
    artifacts: list[VideoArtifact]
    speakers: list[SpeakerVerdict]
    analysis: str


class SceneCheck(Contract):
    attempt: int
    format: FormatCheck
    asr_model: str
    lines: list[LineCheck]
    judgment: SceneJudgment | None
    verdict: SceneVerdict
    reasons: list[str]
    mismatched_words: int
    ignored_speech: list[IgnoredSpeech] = Field(default_factory=list)
