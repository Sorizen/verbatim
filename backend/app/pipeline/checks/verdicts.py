from statistics import mean

from app.constants import (
    CRITIC_PASS_SCORE,
    JUDGE_PASS_SCORE,
    MAX_SCENE_ATTEMPTS,
    PORTRAIT_REJECT_BELOW,
    PRESENCE_PASS_SCORE,
    REBUILD_ATTEMPT,
)
from app.enums import PortraitVerdict, SceneVerdict, ScriptVerdict, SpeakerVisibility
from app.pipeline.contracts import CritiqueDraft, FormatCheck, LineCheck, PortraitScores, RuleViolation, SceneJudgment

ASPECT_REASON = 'the video is not 9:16'
DURATION_REASON = 'the video lasts {seconds} s'
AUDIO_REASON = 'the video has no audio track'
WORDS_REASON = '{shot_id}: heard "{heard}" instead of "{expected}"'
SPEAKER_REASON = '{shot_id}: {speaker} is not the visible speaker'
SPEAKER_REASONS = {
    SpeakerVisibility.OTHER_CHARACTER: '{shot_id}: another character says the line of {speaker}',
    SpeakerVisibility.LIPS_STILL: '{shot_id}: {speaker} faces the camera but the lips do not move',
}
TEXT_REASON = 'text or subtitles are visible in the frame'
VISUAL_REASON = 'visual quality {score:.1f} is below {threshold}'
PRESENCE_REASON = 'the characters on screen do not match the scene'


def decide_script_verdict(violations: list[RuleViolation], review: CritiqueDraft | None) -> ScriptVerdict:
    if violations or not review:
        return ScriptVerdict.REVISE
    scores = (review.hook.score, review.escalation.score, review.ending.score)
    return ScriptVerdict.PASS if min(scores) >= CRITIC_PASS_SCORE else ScriptVerdict.REVISE


def decide_portrait_verdict(scores: PortraitScores) -> PortraitVerdict:
    if min(scores.as_dict().values()) < PORTRAIT_REJECT_BELOW:
        return PortraitVerdict.REDRAW
    return PortraitVerdict.PASS


def format_reasons(check: FormatCheck) -> list[str]:
    reasons = []
    if not check.aspect_ok:
        reasons.append(ASPECT_REASON)
    if not check.duration_ok:
        reasons.append(DURATION_REASON.format(seconds=check.duration_s))
    if not check.has_audio:
        reasons.append(AUDIO_REASON)
    return reasons


def line_reasons(lines: list[LineCheck]) -> list[str]:
    reasons = []
    for line in lines:
        if line.diff:
            reasons.append(WORDS_REASON.format(shot_id=line.shot_id, heard=line.heard, expected=line.expected))
        if line.speaker_matches is False:
            reasons.append(speaker_reason(line))
    return reasons


def speaker_reason(line: LineCheck) -> str:
    template = (
        SPEAKER_REASONS.get(line.speaker_visibility, SPEAKER_REASON) if line.speaker_visibility else SPEAKER_REASON
    )
    return template.format(shot_id=line.shot_id, speaker=line.speaker)


def judgment_reasons(judgment: SceneJudgment | None) -> list[str]:
    if not judgment:
        return []
    reasons = []
    if judgment.on_screen_text:
        reasons.append(TEXT_REASON)
    visual = mean((judgment.physics_integrity, judgment.temporal_continuity, judgment.reaction_plausibility))
    if visual < JUDGE_PASS_SCORE:
        reasons.append(VISUAL_REASON.format(score=visual, threshold=JUDGE_PASS_SCORE))
    if judgment.character_presence_consistency < PRESENCE_PASS_SCORE:
        reasons.append(PRESENCE_REASON)
    return reasons


def first_failed_line(lines: list[LineCheck]) -> LineCheck | None:
    return next((line for line in lines if line.diff or line.speaker_matches is False), None)


def decide_scene_verdict(
    *,
    attempt: int,
    format_check: FormatCheck,
    lines: list[LineCheck],
    judgment: SceneJudgment | None,
) -> tuple[SceneVerdict, list[str]]:
    reasons = [*format_reasons(format_check), *line_reasons(lines), *judgment_reasons(judgment)]
    if not reasons:
        return SceneVerdict.PASS, reasons
    if attempt >= MAX_SCENE_ATTEMPTS:
        return SceneVerdict.NEEDS_REVIEW, reasons
    if attempt + 1 == REBUILD_ATTEMPT and first_failed_line(lines):
        return SceneVerdict.REBUILD_SHOT, reasons
    return SceneVerdict.RETRY, reasons
