
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str
    version: str


class ErrorDetail(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: list[ErrorDetail] | None = None
