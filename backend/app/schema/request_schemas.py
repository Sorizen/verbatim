from pydantic import BaseModel, Field

from app.constants import MAX_IDEA_LENGTH, MIN_IDEA_LENGTH


class CreateRunRequest(BaseModel):
    idea: str = Field(min_length=MIN_IDEA_LENGTH, max_length=MAX_IDEA_LENGTH)


class ReviewDecisionRequest(BaseModel):
    approve: bool
