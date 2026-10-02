from fastapi import APIRouter, Query, status
from fastapi.responses import FileResponse

from app.constants import DEFAULT_RUNS_LIMIT, MAX_RUNS_LIMIT, RUNS_TAG, VIDEO_MEDIA_TYPE
from app.schema import CreateRunRequest, ReviewDecisionRequest, RunLinesResponse, RunListResponse, RunSchema
from app.services import RunServiceDep

router = APIRouter(tags=[RUNS_TAG])


@router.post('/runs', response_model=RunSchema, status_code=status.HTTP_201_CREATED)
async def create_run(request: CreateRunRequest, run_service: RunServiceDep) -> RunSchema:
    return await run_service.create_run(idea=request.idea)


@router.get('/runs', response_model=RunListResponse)
async def list_runs(
    run_service: RunServiceDep,
    limit: int = Query(DEFAULT_RUNS_LIMIT, ge=1, le=MAX_RUNS_LIMIT),
) -> RunListResponse:
    return RunListResponse(items=await run_service.list_runs(limit=limit))


@router.get('/runs/{run_id}', response_model=RunSchema)
async def get_run(run_id: str, run_service: RunServiceDep) -> RunSchema:
    return await run_service.get_run(run_id)


@router.get('/runs/{run_id}/lines', response_model=RunLinesResponse)
async def get_run_lines(run_id: str, run_service: RunServiceDep) -> RunLinesResponse:
    return RunLinesResponse(items=await run_service.get_lines(run_id))


@router.get('/runs/{run_id}/video', response_class=FileResponse)
async def get_run_video(run_id: str, run_service: RunServiceDep) -> FileResponse:
    path = await run_service.get_video_path(run_id)
    return FileResponse(path, media_type=VIDEO_MEDIA_TYPE, filename=f'{run_id}.mp4')


@router.post('/runs/{run_id}/review', response_model=RunSchema)
async def review_run(run_id: str, request: ReviewDecisionRequest, run_service: RunServiceDep) -> RunSchema:
    return await run_service.submit_review(run_id, approve=request.approve)


@router.post('/runs/{run_id}/continue', response_model=RunSchema)
async def continue_run(run_id: str, run_service: RunServiceDep) -> RunSchema:
    return await run_service.continue_run(run_id)
