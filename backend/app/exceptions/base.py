from fastapi import status


class BaseError(Exception):
    code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = 'Internal error'
