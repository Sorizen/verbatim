from pathlib import Path
from typing import Any

from langgraph.runtime import Runtime

from app.constants import SCENE_CHECK_FILE_TEMPLATE, SPEECH_MODEL, TAKE_AUDIO_FILE_TEMPLATE, TAKE_FILE_TEMPLATE
from app.enums import SceneVerdict, StepName
from app.media import extract_audio, probe_media
from app.pipeline.checks import (
    build_format_check,
    decide_scene_verdict,
    drop_phantom_speech,
    expected_words,
    map_transcript_to_lines,
)
from app.pipeline.checks.judge_windows import apply_speaker_verdicts, cut_judge_windows
from app.pipeline.contracts import Scene, SceneCheck
from app.pipeline.graph.context import PipelineContext
from app.pipeline.graph.state import PipelineState
from app.providers.types import Transcript

REASONS_SEPARATOR = '; '
PASSED_NOTE = 'every line was heard word for word'


async def transcribe_take(context: PipelineContext, take: Path, attempt: int) -> Transcript:
    audio = await extract_audio(take, context.workspace.resolve(TAKE_AUDIO_FILE_TEMPLATE.format(attempt=attempt)))
    return await context.providers.speech.transcribe(model=SPEECH_MODEL, audio_path=audio)


def portrait_paths(context: PipelineContext, scene: Scene) -> dict[str, Path]:
    return {character.id: context.workspace.resolve(character.portrait) for character in scene.characters}


async def scene_check_node(state: PipelineState, runtime: Runtime[PipelineContext]) -> dict[str, Any]:
    context = runtime.context
    scene = state.require_scene()
    attempt = state.attempt
    take = context.workspace.resolve(TAKE_FILE_TEMPLATE.format(attempt=attempt))
    async with context.reporter.step(StepName.SCENE_CHECK, attempt) as step:
        format_check = build_format_check(await probe_media(take))
        transcript = await transcribe_take(context, take, attempt)
        step.add_cost(transcript.cost_usd)
        script = state.require_script()
        transcript, ignored = drop_phantom_speech(transcript, expected_words(script))
        lines = map_transcript_to_lines(script, transcript)
        windows = await cut_judge_windows(context.workspace, take, lines, attempt)
        judged = await context.crew.scene_judge.judge(
            scene=scene, portraits=portrait_paths(context, scene), windows=windows
        )
        step.add_cost(judged.cost_usd)
        lines = apply_speaker_verdicts(lines, judged.value)
        verdict, reasons = decide_scene_verdict(
            attempt=attempt, format_check=format_check, lines=lines, judgment=judged.value
        )
        check = SceneCheck(
            attempt=attempt,
            format=format_check,
            asr_model=SPEECH_MODEL,
            lines=lines,
            judgment=judged.value,
            verdict=verdict,
            reasons=reasons,
            mismatched_words=sum(len(line.diff) for line in lines),
            ignored_speech=ignored,
        )
        context.workspace.write_json(SCENE_CHECK_FILE_TEMPLATE.format(attempt=attempt), check)
        if verdict == SceneVerdict.PASS:
            step.note(PASSED_NOTE)
        else:
            step.reject(REASONS_SEPARATOR.join(reasons))
    return {'scene_checks': [*state.scene_checks, check]}
