import base64
from pathlib import Path

DATA_URL_TEMPLATE = 'data:{mime_type};base64,{payload}'


def file_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def file_to_data_url(path: Path, mime_type: str) -> str:
    return DATA_URL_TEMPLATE.format(mime_type=mime_type, payload=file_to_base64(path))
