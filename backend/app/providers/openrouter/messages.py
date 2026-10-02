from typing import Any

from app.providers.types import AudioPart, ChatMessage, ContentPart, ImagePart, TextPart

SYSTEM_ROLE = 'system'


def serialize_part(part: ContentPart) -> dict[str, Any]:
    if isinstance(part, TextPart):
        return {'type': 'text', 'text': part.text}
    if isinstance(part, ImagePart):
        return {'type': 'image_url', 'image_url': {'url': part.data_url}}
    if isinstance(part, AudioPart):
        return {'type': 'input_audio', 'input_audio': {'data': part.data_base64, 'format': part.audio_format}}
    raise TypeError(f'unsupported content part: {part!r}')


def serialize_message(message: ChatMessage) -> dict[str, Any]:
    if message.role == SYSTEM_ROLE:
        text = ''.join(part.text for part in message.parts if isinstance(part, TextPart))
        return {'role': message.role, 'content': text}
    return {'role': message.role, 'content': [serialize_part(part) for part in message.parts]}
