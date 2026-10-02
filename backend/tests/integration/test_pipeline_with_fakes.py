from collections.abc import Callable

import pytest

from app.enums import RunStatus, SceneVerdict
from app.exceptions import ProviderError
from app.pipeline.contracts import Script
from tests.conftest import PipelineHarness
from tests.fakes import FakeVideos

LOCKED_LINE = 'Nice hat, big man. Did your mother pick it out?'
IDEA = f'A man walks into a saloon and tells a big guy: "{LOCKED_LINE}" A fight starts.'

type HarnessFactory = Callable[..., PipelineHarness]


async def test_happy_path_keeps_quoted_line_verbatim(make_harness: HarnessFactory) -> None:
    harness = make_harness()
    result = await harness.run(IDEA)
    assert result.status == RunStatus.DONE
    assert result.final_video and result.final_video.is_file()
    script = harness.workspace.read_json('script.json', Script)
    assert script
    assert script.shots[0].line
    assert script.shots[0].line.text == LOCKED_LINE
    assert script.shots[0].line.locked
    request = harness.workspace.resolve('requests/1.json').read_text()
    assert LOCKED_LINE in request


async def test_dropped_word_triggers_one_retry(make_harness: HarnessFactory) -> None:
    harness = make_harness(flaky_submissions=frozenset({1}))
    result = await harness.run(IDEA)
    state = await harness.state()
    assert result.status == RunStatus.DONE
    assert [check.verdict for check in state.scene_checks] == [SceneVerdict.RETRY, SceneVerdict.PASS]


async def test_second_failure_rebuilds_the_shot_with_the_same_words(make_harness: HarnessFactory) -> None:
    harness = make_harness(flaky_submissions=frozenset({1, 2}))
    result = await harness.run(IDEA)
    state = await harness.state()
    assert result.status == RunStatus.DONE
    assert [check.verdict for check in state.scene_checks] == [
        SceneVerdict.RETRY,
        SceneVerdict.REBUILD_SHOT,
        SceneVerdict.PASS,
    ]
    assert state.shot_fix
    assert state.scene
    rebuilt = next(shot for shot in state.scene.shots if shot.id == state.shot_fix.shot_id)
    assert rebuilt.dialogue
    assert rebuilt.dialogue.text == LOCKED_LINE


async def test_three_failures_pause_for_a_human_who_approves(make_harness: HarnessFactory) -> None:
    harness = make_harness(flaky_submissions=frozenset({1, 2, 3}))
    paused = await harness.run(IDEA)
    assert paused.status == RunStatus.NEEDS_REVIEW
    assert paused.final_video and paused.final_video.is_file()
    assert paused.review_reason
    approved = await harness.resume(approve=True)
    assert approved.status == RunStatus.DONE


async def test_reviewer_can_reject_the_best_take(make_harness: HarnessFactory) -> None:
    harness = make_harness(flaky_submissions=frozenset({1, 2, 3}))
    await harness.run(IDEA)
    rejected = await harness.resume(approve=False)
    assert rejected.status == RunStatus.FAILED
    assert rejected.final_video is None


async def test_failed_video_job_continues_from_the_shoot(make_harness: HarnessFactory) -> None:
    harness = make_harness(failed_submissions=frozenset({1}))
    with pytest.raises(ProviderError):
        await harness.run(IDEA)
    script_before = harness.workspace.resolve('script.json').stat().st_mtime_ns
    result = await harness.continue_run()
    state = await harness.state()
    videos = harness.providers.videos
    assert isinstance(videos, FakeVideos)
    assert result.status == RunStatus.DONE
    assert [attempt.attempt for attempt in state.attempts] == [1]
    assert videos.submissions == 2
    assert harness.workspace.resolve('script.json').stat().st_mtime_ns == script_before
