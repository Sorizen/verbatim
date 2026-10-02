from typing import Any

from langgraph.runtime import Runtime

from app.constants import (
    FINAL_VIDEO_FILE,
    IMAGE_MODEL,
    JUDGE_MODEL,
    LLM_MODEL,
    MANIFEST_FILE,
    SPEECH_MODEL,
    TAKE_FILE_TEMPLATE,
    VIDEO_MODEL,
)
from app.enums import RunStatus, SceneVerdict, StepName
from app.pipeline.contracts import Manifest, SceneCheck
from app.pipeline.graph.context import PipelineContext
from app.pipeline.graph.state import PipelineState, RunOutcome

REVIEW_REASON_TEMPLATE = 'No take passed the check. The best is take {attempt}: {reasons}'
REASONS_SEPARATOR = '; '
FINAL_NOTE_TEMPLATE = 'attempt {attempt} -> {status}'
MODELS = {
    'llm': LLM_MODEL,
    'images': IMAGE_MODEL,
    'video': VIDEO_MODEL,
    'speech': SPEECH_MODEL,
    'judge': JUDGE_MODEL,
}


def pick_best_check(checks: list[SceneCheck]) -> SceneCheck:
    return min(checks, key=lambda check: (check.mismatched_words, len(check.reasons), check.attempt))


def build_outcome(checks: list[SceneCheck], final_video: str) -> RunOutcome:
    passed = next((check for check in reversed(checks) if check.verdict == SceneVerdict.PASS), None)
    if passed:
        return RunOutcome(
            status=RunStatus.DONE, final_video=final_video, best_attempt=passed.attempt, review_reason=None
        )
    best = pick_best_check(checks)
    reason = REVIEW_REASON_TEMPLATE.format(attempt=best.attempt, reasons=REASONS_SEPARATOR.join(best.reasons))
    return RunOutcome(
        status=RunStatus.NEEDS_REVIEW, final_video=final_video, best_attempt=best.attempt, review_reason=reason
    )


def write_manifest(context: PipelineContext, state: PipelineState, outcome: RunOutcome) -> None:
    manifest = Manifest(
        run_id=state.run_id,
        idea=state.idea,
        status=outcome.status,
        final_path=outcome.final_video,
        best_attempt=outcome.best_attempt,
        models=MODELS,
        cost_usd=round(context.budget.spent_usd, 4),
        review_reason=outcome.review_reason,
    )
    context.workspace.write_json(MANIFEST_FILE, manifest)


async def finalize_node(state: PipelineState, runtime: Runtime[PipelineContext]) -> dict[str, Any]:
    context = runtime.context
    async with context.reporter.step(StepName.FINAL) as step:
        outcome = build_outcome(state.scene_checks, FINAL_VIDEO_FILE)
        take = context.workspace.resolve(TAKE_FILE_TEMPLATE.format(attempt=outcome.best_attempt))
        context.workspace.copy_file(take, FINAL_VIDEO_FILE)
        write_manifest(context, state, outcome)
        step.note(FINAL_NOTE_TEMPLATE.format(attempt=outcome.best_attempt, status=outcome.status.value))
    return {'outcome': outcome}
