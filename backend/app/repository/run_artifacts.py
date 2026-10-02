import re
from pathlib import Path

from app.config import settings
from app.constants import BRIEF_FILE, MANIFEST_FILE, SCENE_CHECK_FILE_TEMPLATE, SCRIPT_FILE
from app.pipeline.contracts import Brief, Manifest, SceneCheck, Script
from app.pipeline.storage import RunWorkspace

SCENE_CHECK_PATTERN = re.compile(r'^judge-(\d+)\.json$')
SCENE_CHECK_GLOB = 'judge-*.json'


def latest_check_name(run_dir: Path) -> str | None:
    numbered = [
        (int(match.group(1)), path.name)
        for path in run_dir.glob(SCENE_CHECK_GLOB)
        if (match := SCENE_CHECK_PATTERN.match(path.name))
    ]
    if not numbered:
        return None
    return max(numbered)[1]


class RunArtifactsRepository:
    def __init__(self, run_id: str) -> None:
        self.workspace = RunWorkspace.for_run(settings.RUNS_DIR, run_id)

    def resolve_stored_file(self, stored_path: str) -> Path:
        return self.workspace.resolve(Path(stored_path).name)

    def read_brief(self) -> Brief | None:
        return self.workspace.read_json(BRIEF_FILE, Brief)

    def read_script(self) -> Script | None:
        return self.workspace.read_json(SCRIPT_FILE, Script)

    def read_manifest(self) -> Manifest | None:
        return self.workspace.read_json(MANIFEST_FILE, Manifest)

    def read_scene_check(self, attempt: int) -> SceneCheck | None:
        return self.workspace.read_json(SCENE_CHECK_FILE_TEMPLATE.format(attempt=attempt), SceneCheck)

    def read_latest_scene_check(self) -> SceneCheck | None:
        name = latest_check_name(self.workspace.root)
        if not name:
            return None
        return self.workspace.read_json(name, SceneCheck)
