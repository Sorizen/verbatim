import asyncio
import secrets
import time
from typing import Any

from langgraph.runtime import Runtime

from app.constants import (
    ATTEMPT_FILE_TEMPLATE,
    JPEG_MIME_TYPE,
    MAX_SEED,
    REQUEST_FILE_TEMPLATE,
    TAKE_FILE_TEMPLATE,
    VIDEO_POLL_INTERVAL_SECONDS,
    VIDEO_POLL_TIMEOUT_SECONDS,
)
from app.enums import StepName, VideoJobStatus
from app.exceptions import ProviderError, ProviderTimeoutError
from app.pipeline.adapters import build_wan_request
from app.pipeline.budget import estimate_video_cost
from app.pipeline.contracts import RenderAttempt, Scene
from app.pipeline.graph.context import PipelineContext
from app.pipeline.graph.state import PipelineState
from app.providers.protocols import VideoClient
from app.providers.types import VideoJob
from app.utils import file_to_data_url

FAILED_JOB_STATUSES = frozenset({VideoJobStatus.FAILED, VideoJobStatus.CANCELLED, VideoJobStatus.EXPIRED})
TERMINAL_STATUSES = FAILED_JOB_STATUSES | {VideoJobStatus.COMPLETED}
JOB_FAILED_TEMPLATE = 'video job {job_id} ended with {status}: {error}'
JOB_TIMEOUT_TEMPLATE = 'video job {job_id} did not finish in {seconds:.0f} s'
RENDER_NOTE_TEMPLATE = 'seed {seed}, job {job_id}'


async def wait_for_job(videos: VideoClient, job_id: str) -> VideoJob:
    deadline = time.monotonic() + VIDEO_POLL_TIMEOUT_SECONDS
    while True:
        job = await videos.poll(job_id)
        if job.status in TERMINAL_STATUSES:
            return job
        if time.monotonic() > deadline:
            raise ProviderTimeoutError(JOB_TIMEOUT_TEMPLATE.format(job_id=job_id, seconds=VIDEO_POLL_TIMEOUT_SECONDS))
        await asyncio.sleep(VIDEO_POLL_INTERVAL_SECONDS)


async def submit_attempt(context: PipelineContext, scene: Scene, attempt: int) -> RenderAttempt:
    estimate = estimate_video_cost(scene.format.resolution, scene.format.duration_s)
    context.budget.ensure_room(estimate)
    seed = secrets.randbelow(MAX_SEED)
    references = [
        file_to_data_url(context.workspace.resolve(character.portrait), JPEG_MIME_TYPE)
        for character in scene.characters
    ]
    request = build_wan_request(scene, reference_images=references, seed=seed)
    request_path = REQUEST_FILE_TEMPLATE.format(attempt=attempt)
    readable_request = request.model_copy(
        update={'reference_images': [character.portrait for character in scene.characters]}
    )
    context.workspace.write_json(request_path, readable_request)
    job = await context.providers.videos.submit(request)
    record = RenderAttempt(
        attempt=attempt,
        model=request.model,
        request_path=request_path,
        seed=seed,
        job_id=job.job_id,
        status=job.status,
        video_path=None,
        cost_usd=estimate,
    )
    context.workspace.write_json(ATTEMPT_FILE_TEMPLATE.format(attempt=attempt), record)
    return record


async def load_or_submit(context: PipelineContext, scene: Scene, attempt: int) -> RenderAttempt:
    record = context.workspace.read_json(ATTEMPT_FILE_TEMPLATE.format(attempt=attempt), RenderAttempt)
    if record and record.status not in FAILED_JOB_STATUSES:
        return record
    return await submit_attempt(context, scene, attempt)


async def render_attempt(context: PipelineContext, scene: Scene, attempt: int) -> RenderAttempt:
    attempt_path = ATTEMPT_FILE_TEMPLATE.format(attempt=attempt)
    record = await load_or_submit(context, scene, attempt)
    job = await wait_for_job(context.providers.videos, record.job_id)
    if job.status != VideoJobStatus.COMPLETED:
        context.workspace.write_json(attempt_path, record.model_copy(update={'status': job.status}))
        raise ProviderError(JOB_FAILED_TEMPLATE.format(job_id=job.job_id, status=job.status.value, error=job.error))
    take_path = TAKE_FILE_TEMPLATE.format(attempt=attempt)
    await context.providers.videos.download(job.job_id, context.workspace.resolve(take_path))
    completed = record.model_copy(
        update={
            'status': job.status,
            'video_path': take_path,
            'cost_usd': job.cost_usd if job.cost_usd is not None else record.cost_usd,
        }
    )
    context.workspace.write_json(attempt_path, completed)
    return completed


async def render_node(state: PipelineState, runtime: Runtime[PipelineContext]) -> dict[str, Any]:
    context = runtime.context
    attempt = state.attempt + 1
    async with context.reporter.step(StepName.RENDER, attempt) as step:
        record = await render_attempt(context, state.require_scene(), attempt)
        step.add_cost(record.cost_usd)
        step.note(RENDER_NOTE_TEMPLATE.format(seed=record.seed, job_id=record.job_id))
    return {'attempt': attempt, 'attempts': [*state.attempts, record]}
