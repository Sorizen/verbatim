from pydantic import Field

from app.pipeline.contracts.base import Contract


class CastMember(Contract):
    id: str = Field(description='Character id from the brief')
    look: str = Field(description='Face, age, build and hair; specific and visual')
    wardrobe: str
    voice: str = Field(description='Timbre, accent and pace, for example "deep, rough male voice"')
    portrait_prompt: str = Field(
        description=(
            'Prompt for one photoreal vertical portrait: one person, face clearly visible, plain background, no text'
        )
    )


class Cast(Contract):
    characters: list[CastMember]

    def member(self, character_id: str) -> CastMember:
        return next(member for member in self.characters if member.id == character_id)


class Portrait(Contract):
    character_id: str
    path: str
    attempt: int
