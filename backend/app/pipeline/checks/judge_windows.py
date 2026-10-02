from pathlib import Path

from app.constants import (
    JUDGE_FRAME_WIDTH,
    JUDGE_FRAMES_PER_SECOND,
    JUDGE_WINDOW_PADDING_SECONDS,
    MAX_JUDGE_FRAMES_PER_WINDOW,
    WINDOW_AUDIO_FILE,
    WINDOW_DIR_TEMPLATE,
)
from app.enums import SpeakerVisibility
from app.media import extract_audio_window, extract_frames
from app.pipeline.agents import JudgeWindow
from app.pipeline.contracts import LineCheck, SceneJudgment
from app.pipeline.storage import RunWorkspace

SPEAKER_PASSES = frozenset({SpeakerVisibility.ON_SCREEN, SpeakerVisibility.UNSEEN})


def sample_evenly(frames: list[Path], limit: int) -> list[Path]:
    if len(frames) <= limit:
        return frames
    step = len(frames) / limit
    return [frames[int(index * step)] for index in range(limit)]


async def cut_window(take: Path, line: LineCheck, start_s: float, end_s: float, directory: Path) -> JudgeWindow:
    frames = await extract_frames(
        take,
        start_s=start_s,
        end_s=end_s,
        frames_per_second=JUDGE_FRAMES_PER_SECOND,
        width=JUDGE_FRAME_WIDTH,
        destination_dir=directory,
    )
    audio = await extract_audio_window(take, start_s=start_s, end_s=end_s, destination=directory / WINDOW_AUDIO_FILE)
    return JudgeWindow(
        shot_id=line.shot_id,
        speaker=line.speaker,
        start_s=start_s,
        end_s=end_s,
        frames=sample_evenly(frames, MAX_JUDGE_FRAMES_PER_WINDOW),
        audio=audio,
    )


async def cut_judge_windows(
    workspace: RunWorkspace,
    take: Path,
    lines: list[LineCheck],
    attempt: int,
) -> list[JudgeWindow]:
    windows = []
    for line in lines:
        if line.start_s is None or line.end_s is None:
            continue
        directory = workspace.resolve(WINDOW_DIR_TEMPLATE.format(attempt=attempt, shot_id=line.shot_id))
        start_s = max(line.start_s - JUDGE_WINDOW_PADDING_SECONDS, 0.0)
        end_s = line.end_s + JUDGE_WINDOW_PADDING_SECONDS
        windows.append(await cut_window(take, line, start_s, end_s, directory))
    return windows


def apply_speaker_verdicts(lines: list[LineCheck], judgment: SceneJudgment) -> list[LineCheck]:
    verdicts = {verdict.shot_id: verdict.visibility for verdict in judgment.speakers}
    return [with_visibility(line, verdicts.get(line.shot_id)) for line in lines]


def with_visibility(line: LineCheck, visibility: SpeakerVisibility | None) -> LineCheck:
    matches = visibility in SPEAKER_PASSES if visibility else None
    return line.model_copy(update={'speaker_visibility': visibility, 'speaker_matches': matches})
