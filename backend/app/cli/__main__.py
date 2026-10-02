import argparse
import asyncio
import sys

from app.enums import RunStatus
from app.exceptions import PipelineError
from app.pipeline.local_runner import run_locally

DESCRIPTION = 'Turn a 1-3 sentence idea into a vertical micro-scene with verbatim dialogue.'
EXIT_CODES = {RunStatus.DONE: 0, RunStatus.FAILED: 1, RunStatus.NEEDS_REVIEW: 2}
FAILED_TEMPLATE = 'failed: {message}\n'
SUMMARY_TEMPLATE = '\nrun {run_id}: {status}\nvideo: {video}\n'
REASON_TEMPLATE = 'reason: {reason}\n'
NO_VIDEO = 'none'


def main() -> int:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('idea', help='the idea in one to three sentences, quoted lines are kept word for word')
    arguments = parser.parse_args()
    try:
        run_id, result = asyncio.run(run_locally(arguments.idea))
    except PipelineError as error:
        sys.stderr.write(FAILED_TEMPLATE.format(message=error.message))
        return EXIT_CODES[RunStatus.FAILED]
    video = str(result.final_video) if result.final_video else NO_VIDEO
    sys.stdout.write(SUMMARY_TEMPLATE.format(run_id=run_id, status=result.status.value, video=video))
    if result.review_reason:
        sys.stdout.write(REASON_TEMPLATE.format(reason=result.review_reason))
    return EXIT_CODES[result.status]


if __name__ == '__main__':
    raise SystemExit(main())
