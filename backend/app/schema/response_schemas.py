from pydantic import BaseModel

from app.schema.line_report import LineReportSchema
from app.schema.run import RunSummarySchema


class RunListResponse(BaseModel):
    items: list[RunSummarySchema]


class HealthResponse(BaseModel):
    status: str


class RunLinesResponse(BaseModel):
    items: list[LineReportSchema]
