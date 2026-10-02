from pydantic import BaseModel, ConfigDict, TypeAdapter


class SpokenLine(BaseModel):
    model_config = ConfigDict(frozen=True)

    text: str
    start: float
    end: float


SPOKEN_LINES_ADAPTER = TypeAdapter(list[SpokenLine])
