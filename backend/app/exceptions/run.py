from fastapi import status

from app.constants import MISSING_API_KEY_MESSAGE
from app.exceptions.base import BaseError


class RunNotFoundError(BaseError):
    code = status.HTTP_404_NOT_FOUND
    message = 'Run not found'


class VideoNotReadyError(BaseError):
    code = status.HTTP_409_CONFLICT
    message = 'Video is not ready yet'


class RunCannotContinueError(BaseError):
    code = status.HTTP_409_CONFLICT
    message = 'Only a run that stopped on an error can continue'


class RunNotAwaitingReviewError(BaseError):
    code = status.HTTP_409_CONFLICT
    message = 'Run is not waiting for a review'


class MissingApiKeyError(BaseError):
    code = status.HTTP_503_SERVICE_UNAVAILABLE
    message = MISSING_API_KEY_MESSAGE
