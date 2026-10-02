from pathlib import Path

from app.constants import VIDEO_CONTENT_PATH_TEMPLATE, VIDEO_JOB_PATH_TEMPLATE, VIDEOS_PATH
from app.providers.openrouter.http import OpenRouterHttp
from app.providers.openrouter.schemas import VideoJobResponse
from app.providers.types import VideoJob, VideoRequest

FIRST_OUTPUT_INDEX = 0


def to_video_job(response: VideoJobResponse) -> VideoJob:
    cost = response.usage.cost if response.usage else None
    return VideoJob(job_id=response.id, status=response.status, cost_usd=cost, error=response.error)


class OpenRouterVideos:
    def __init__(self, http: OpenRouterHttp) -> None:
        self._http = http

    async def submit(self, request: VideoRequest) -> VideoJob:
        body = {
            'model': request.model,
            'prompt': request.prompt,
            'duration': request.duration_s,
            'resolution': request.resolution.value,
            'aspect_ratio': request.aspect_ratio,
            'generate_audio': request.generate_audio,
            'seed': request.seed,
            'input_references': [{'type': 'image_url', 'image_url': {'url': url}} for url in request.reference_images],
        }
        return to_video_job(VideoJobResponse.model_validate(await self._http.post_json(VIDEOS_PATH, body)))

    async def poll(self, job_id: str) -> VideoJob:
        payload = await self._http.get_json(VIDEO_JOB_PATH_TEMPLATE.format(job_id=job_id))
        return to_video_job(VideoJobResponse.model_validate(payload))

    async def download(self, job_id: str, destination: Path) -> None:
        await self._http.download(
            VIDEO_CONTENT_PATH_TEMPLATE.format(job_id=job_id), destination, params={'index': FIRST_OUTPUT_INDEX}
        )
