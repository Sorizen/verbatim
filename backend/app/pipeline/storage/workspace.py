import shutil
from pathlib import Path

from pydantic import BaseModel

JSON_INDENT = 2


class RunWorkspace:
    def __init__(self, root: Path) -> None:
        self.root = root

    @classmethod
    def for_run(cls, runs_dir: Path, run_id: str) -> 'RunWorkspace':
        return cls(runs_dir / run_id)

    def resolve(self, relative: str) -> Path:
        return self.root / relative

    def relative(self, path: Path) -> str:
        return str(path.relative_to(self.root))

    def write_json(self, relative: str, value: BaseModel) -> Path:
        path = self._prepare(relative)
        path.write_text(value.model_dump_json(indent=JSON_INDENT))
        return path

    def read_json[T: BaseModel](self, relative: str, schema: type[T]) -> T | None:
        path = self.resolve(relative)
        if not path.is_file():
            return None
        return schema.model_validate_json(path.read_text())

    def write_bytes(self, relative: str, data: bytes) -> Path:
        path = self._prepare(relative)
        path.write_bytes(data)
        return path

    def copy_file(self, source: Path, relative: str) -> Path:
        path = self._prepare(relative)
        shutil.copyfile(source, path)
        return path

    def _prepare(self, relative: str) -> Path:
        path = self.resolve(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
