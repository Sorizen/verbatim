from typing import Annotated, Protocol

from fastapi import Depends

from app.worker.tasks import continue_pipeline_task, resume_pipeline_task, run_pipeline_task


class PipelineQueue(Protocol):
    def enqueue_run(self, run_id: str) -> None: ...

    def enqueue_review(self, run_id: str, *, approve: bool) -> None: ...

    def enqueue_continue(self, run_id: str) -> None: ...


class CeleryPipelineQueue:
    def enqueue_run(self, run_id: str) -> None:
        run_pipeline_task.delay(run_id)

    def enqueue_review(self, run_id: str, *, approve: bool) -> None:
        resume_pipeline_task.delay(run_id, approve)

    def enqueue_continue(self, run_id: str) -> None:
        continue_pipeline_task.delay(run_id)


def get_pipeline_queue() -> PipelineQueue:
    return CeleryPipelineQueue()


PipelineQueueDep = Annotated[PipelineQueue, Depends(get_pipeline_queue)]
