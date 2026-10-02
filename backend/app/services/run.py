from pathlib import Path
from typing import Annotated

import anyio
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.constants import VIDEO_URL_TEMPLATE
from app.db import get_db
from app.enums import RunStatus
from app.exceptions import (
    MissingApiKeyError,
    RunCannotContinueError,
    RunNotAwaitingReviewError,
    RunNotFoundError,
    VideoNotReadyError,
)
from app.models import Run
from app.pipeline.contracts import SceneCheck
from app.repository import RunArtifactsRepository, RunRepository
from app.schema import LineReportSchema, RunSchema, RunSummarySchema
from app.services.run_lines import build_line_reports
from app.worker.queue import PipelineQueue, PipelineQueueDep


def build_video_url(run: Run) -> str | None:
    if not run.video_path:
        return None
    return VIDEO_URL_TEMPLATE.format(run_id=run.id)


def can_continue(run: Run) -> bool:
    return run.status == RunStatus.FAILED and run.error is not None


def to_run_schema(run: Run) -> RunSchema:
    return RunSchema.model_validate(run).model_copy(
        update={'video_url': build_video_url(run), 'can_continue': can_continue(run)}
    )


def to_run_summary(run: Run) -> RunSummarySchema:
    return RunSummarySchema.model_validate(run).model_copy(update={'video_url': build_video_url(run)})


def read_shown_check(artifacts: RunArtifactsRepository) -> SceneCheck | None:
    manifest = artifacts.read_manifest()
    if manifest and manifest.best_attempt:
        return artifacts.read_scene_check(manifest.best_attempt)
    return artifacts.read_latest_scene_check()


def read_line_reports(run_id: str) -> list[LineReportSchema]:
    artifacts = RunArtifactsRepository(run_id)
    return build_line_reports(artifacts.read_brief(), artifacts.read_script(), read_shown_check(artifacts))


class RunService:
    def __init__(self, db: AsyncSession, queue: PipelineQueue) -> None:
        self.db = db
        self.queue = queue
        self.run_repository = RunRepository(db)

    async def create_run(self, idea: str) -> RunSchema:
        if not settings.OPENROUTER_API_KEY.get_secret_value():
            raise MissingApiKeyError()
        run = await self.run_repository.create(idea=idea.strip())
        await self.db.commit()
        await run_in_threadpool(self.queue.enqueue_run, run.id)
        return await self.get_run(run.id)

    async def get_run(self, run_id: str) -> RunSchema:
        return to_run_schema(await self._get_existing_run(run_id))

    async def list_runs(self, limit: int) -> list[RunSummarySchema]:
        runs = await self.run_repository.list_recent(limit=limit)
        return [to_run_summary(run) for run in runs]

    async def get_video_path(self, run_id: str) -> Path:
        run = await self._get_existing_run(run_id)
        if not run.video_path:
            raise VideoNotReadyError()
        path = RunArtifactsRepository(run_id).resolve_stored_file(run.video_path)
        if not await anyio.Path(path).is_file():
            raise VideoNotReadyError()
        return path

    async def get_lines(self, run_id: str) -> list[LineReportSchema]:
        await self._get_existing_run(run_id)
        return await run_in_threadpool(read_line_reports, run_id)

    async def submit_review(self, run_id: str, *, approve: bool) -> RunSchema:
        run = await self._get_existing_run(run_id)
        if run.status != RunStatus.NEEDS_REVIEW:
            raise RunNotAwaitingReviewError()
        await self.run_repository.mark_status(run_id, RunStatus.QUEUED, video_path=run.video_path)
        await self.db.commit()
        await run_in_threadpool(self.queue.enqueue_review, run_id, approve=approve)
        return await self.get_run(run_id)

    async def continue_run(self, run_id: str) -> RunSchema:
        run = await self._get_existing_run(run_id)
        if not can_continue(run):
            raise RunCannotContinueError()
        await self.run_repository.mark_status(run_id, RunStatus.QUEUED)
        await self.db.commit()
        await run_in_threadpool(self.queue.enqueue_continue, run_id)
        return await self.get_run(run_id)

    async def _get_existing_run(self, run_id: str) -> Run:
        run = await self.run_repository.get_by_id(run_id)
        if not run:
            raise RunNotFoundError()
        await self.db.refresh(run, attribute_names=['steps'])
        return run


async def get_run_service(queue: PipelineQueueDep, db: AsyncSession = Depends(get_db)) -> RunService:
    return RunService(db=db, queue=queue)


RunServiceDep = Annotated[RunService, Depends(get_run_service)]
