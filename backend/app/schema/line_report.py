from pydantic import BaseModel

from app.enums import DiffOp


class WordDiffSchema(BaseModel):
    op: DiffOp
    expected: str | None
    heard: str | None


class AlignedWordSchema(BaseModel):
    op: DiffOp | None
    expected: str | None
    heard: str | None


class LineReportSchema(BaseModel):
    shot_id: str
    speaker: str
    speaker_name: str
    text: str
    locked: bool
    attempt: int | None
    heard: str | None
    wer: float | None
    diff: list[WordDiffSchema]
    alignment: list[AlignedWordSchema]
    speaker_matches: bool | None
