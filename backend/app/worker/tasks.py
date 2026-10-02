import asyncio

from app.constants import CONTINUE_PIPELINE_TASK, RESUME_PIPELINE_TASK, RUN_PIPELINE_TASK
from app.pipeline.runner import continue_run, resume_run, start_run
from app.worker.celery_app import celery_app


@celery_app.task(name=RUN_PIPELINE_TASK)
def run_pipeline_task(run_id: str) -> None:
    asyncio.run(start_run(run_id))


@celery_app.task(name=RESUME_PIPELINE_TASK)
def resume_pipeline_task(run_id: str, approve: bool) -> None:
    asyncio.run(resume_run(run_id, approve=approve))


@celery_app.task(name=CONTINUE_PIPELINE_TASK)
def continue_pipeline_task(run_id: str) -> None:
    asyncio.run(continue_run(run_id))
