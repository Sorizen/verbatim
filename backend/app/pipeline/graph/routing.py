from langgraph.graph import END

from app.constants import MAX_PORTRAIT_REDRAWS, MAX_SCRIPT_REVISIONS
from app.enums import NodeName, PortraitVerdict, RunStatus, SceneVerdict, ScriptVerdict
from app.pipeline.graph.state import PipelineState

SCENE_ROUTES = {
    SceneVerdict.PASS: NodeName.FINALIZE,
    SceneVerdict.RETRY: NodeName.RENDER,
    SceneVerdict.REBUILD_SHOT: NodeName.SHOT_FIX,
    SceneVerdict.NEEDS_REVIEW: NodeName.FINALIZE,
}


def after_script_check(state: PipelineState) -> str:
    if state.critique and state.critique.verdict == ScriptVerdict.PASS:
        return NodeName.CAST
    if state.script_revision <= MAX_SCRIPT_REVISIONS:
        return NodeName.SCRIPT
    return NodeName.SCRIPT_REVIEW


def after_script_review(state: PipelineState) -> str:
    return NodeName.CAST if state.review_approved else NodeName.REJECTED


def after_portrait_check(state: PipelineState) -> str:
    if all(check.verdict == PortraitVerdict.PASS for check in state.portrait_checks):
        return NodeName.SCENE
    if state.portrait_round <= MAX_PORTRAIT_REDRAWS:
        return NodeName.PORTRAITS
    return NodeName.PORTRAIT_REVIEW


def after_portrait_review(state: PipelineState) -> str:
    return NodeName.SCENE if state.review_approved else NodeName.REJECTED


def after_scene_check(state: PipelineState) -> str:
    return SCENE_ROUTES[state.require_last_check().verdict]


def after_finalize(state: PipelineState) -> str:
    if state.require_outcome().status == RunStatus.NEEDS_REVIEW:
        return NodeName.TAKE_REVIEW
    return END
