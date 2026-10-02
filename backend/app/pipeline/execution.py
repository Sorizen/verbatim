from dataclasses import dataclass
from pathlib import Path
from typing import Any

from langchain_core.runnables import RunnableConfig

from app.constants import FINAL_VIDEO_FILE
from app.enums import RunStatus
from app.pipeline.graph import PipelineState
from app.pipeline.storage import RunWorkspace

GRAPH_RECURSION_LIMIT = 80
INTERRUPT_KEY = '__interrupt__'
REASON_KEY = 'reason'


@dataclass(frozen=True)
class ExecutionResult:
    status: RunStatus
    review_reason: str | None
    final_video: Path | None


def graph_config(run_id: str) -> RunnableConfig:
    return {'configurable': {'thread_id': run_id}, 'recursion_limit': GRAPH_RECURSION_LIMIT}


def interpret_result(result: dict[str, Any], workspace: RunWorkspace) -> ExecutionResult:
    final = workspace.resolve(FINAL_VIDEO_FILE)
    final_video = final if final.is_file() else None
    interrupts = result.get(INTERRUPT_KEY)
    if interrupts:
        payload: dict[str, str] = interrupts[0].value
        return ExecutionResult(RunStatus.NEEDS_REVIEW, payload.get(REASON_KEY), final_video)
    state = PipelineState.model_validate({key: value for key, value in result.items() if key != INTERRUPT_KEY})
    outcome = state.require_outcome()
    video = final_video if outcome.status == RunStatus.DONE else None
    return ExecutionResult(outcome.status, outcome.review_reason, video)
