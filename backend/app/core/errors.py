
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.common import ErrorDetail, ErrorResponse


logger = logging.getLogger(__name__)


class AppError(Exception):
    """An intentional application error with an HTTP status code."""

    def __init__(
        self,
        status_code: int,
        error: str,
        message: str,
    ) -> None:
        self.status_code = status_code
        self.error = error
        self.message = message
        super().__init__(message)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppError)
    async def handle_app_error(
        request: Request,
        exc: AppError,
    ) -> JSONResponse:
        body = ErrorResponse(
            error=exc.error,
            message=exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=body.model_dump(exclude_none=True),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        details = [
            ErrorDetail(
                field=".".join(
                    str(part)
                    for part in err["loc"]
                    if part != "body"
                ),
                message=err["msg"],
            )
            for err in exc.errors()
        ]

        body = ErrorResponse(
            error="validation_error",
            message="The request data is invalid.",
            details=details,
        )
        return JSONResponse(
            status_code=422,
            content=body.model_dump(exclude_none=True),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Unhandled error on %s %s",
            request.method,
            request.url.path,
        )

        body = ErrorResponse(
            error="internal_error",
            message="Something went wrong on our side. Please try again.",
        )
        return JSONResponse(
            status_code=500,
            content=body.model_dump(exclude_none=True),
        )
