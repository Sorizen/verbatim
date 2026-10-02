import re
import uuid
from pathlib import Path

from app.constants import SECONDS_IN_MINUTE
from app.enums import VideoJobStatus
from app.providers.types import VideoJob, VideoRequest
from tests.fakes.media import render_test_video
from tests.fakes.spoken import SPOKEN_LINES_ADAPTER, SpokenLine

SHOT_HEADER_PATTERN = re.compile(r'^Shot \d+ \((\d+):(\d+)-(\d+):(\d+)\)')
QUOTE_OPENING = ': "'
QUOTE_CLOSING = '"'
SPEECH_PADDING_SECONDS = 0.4
VIDEO_WIDTH = 432
VIDEO_HEIGHT = 768
VIDEO_COLOR = '0x2b2024'
JOB_ID_TEMPLATE = 'fake-{number}-{suffix}'
SUFFIX_LENGTH = 8
FAILED_JOB_ERROR = 'fake provider failure'


def to_seconds(minutes: str, seconds: str) -> int:
    return int(minutes) * SECONDS_IN_MINUTE + int(seconds)


def extract_spoken_lines(prompt: str) -> list[SpokenLine]:
    spoken: list[SpokenLine] = []
    window = (0, 0)
    for line in prompt.splitlines():
        header = SHOT_HEADER_PATTERN.match(line)
        if header:
            start_minutes, start_seconds, end_minutes, end_seconds = header.groups()
            window = (to_seconds(start_minutes, start_seconds), to_seconds(end_minutes, end_seconds))
            continue
        opening = line.rfind(QUOTE_OPENING)
        if opening < 0 or not line.endswith(QUOTE_CLOSING):
            continue
        text = line[opening + len(QUOTE_OPENING) : -len(QUOTE_CLOSING)]
        start, end = window
        spoken.append(SpokenLine(text=text, start=start + SPEECH_PADDING_SECONDS, end=end - SPEECH_PADDING_SECONDS))
    return spoken


def drop_last_word(lines: list[SpokenLine]) -> list[SpokenLine]:
    if not lines:
        return lines
    first, *rest = lines
    shortened = first.model_copy(update={'text': first.text.rsplit(' ', 1)[0]})
    return [shortened, *rest]


class FakeVideos:
    def __init__(
        self, *, flaky_submissions: frozenset[int] = frozenset(), failed_submissions: frozenset[int] = frozenset()
    ) -> None:
        self._flaky_submissions = flaky_submissions
        self._failed_submissions = failed_submissions
        self._submissions = 0
        self._requests: dict[str, tuple[VideoRequest, bool]] = {}
        self._failed_jobs: set[str] = set()

    @property
    def submissions(self) -> int:
        return self._submissions

    async def submit(self, request: VideoRequest) -> VideoJob:
        self._submissions += 1
        job_id = JOB_ID_TEMPLATE.format(number=self._submissions, suffix=uuid.uuid4().hex[:SUFFIX_LENGTH])
        self._requests[job_id] = (request, self._submissions in self._flaky_submissions)
        if self._submissions in self._failed_submissions:
            self._failed_jobs.add(job_id)
        return VideoJob(job_id=job_id, status=VideoJobStatus.PENDING)

    async def poll(self, job_id: str) -> VideoJob:
        if job_id in self._failed_jobs:
            return VideoJob(job_id=job_id, status=VideoJobStatus.FAILED, error=FAILED_JOB_ERROR)
        return VideoJob(job_id=job_id, status=VideoJobStatus.COMPLETED, cost_usd=0.0)

    async def download(self, job_id: str, destination: Path) -> None:
        request, flaky = self._requests[job_id]
        spoken = extract_spoken_lines(request.prompt)
        if flaky:
            spoken = drop_last_word(spoken)
        await render_test_video(
            destination,
            duration_s=request.duration_s,
            width=VIDEO_WIDTH,
            height=VIDEO_HEIGHT,
            color=VIDEO_COLOR,
            comment=SPOKEN_LINES_ADAPTER.dump_json(spoken).decode(),
        )
