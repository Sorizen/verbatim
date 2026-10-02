from typing import cast

from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions import BaseError


async def base_error_handler(_: Request, exc: Exception) -> JSONResponse:
    error = cast(BaseError, exc)
    return JSONResponse(status_code=error.code, content={'detail': error.message})
