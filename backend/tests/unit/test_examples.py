from pathlib import Path

from app.config import settings
from app.enums import RunStatus
from app.services.examples import EXAMPLE_RUNS_DIR, copy_example_files, read_examples

RUN_ID = 'example-run'
MANIFEST_FILE = 'manifest.json'
FINAL_VIDEO_FILE = 'final.mp4'


def test_example_files_are_copied_once(tmp_path: Path) -> None:
    examples_dir = tmp_path / 'examples'
    runs_dir = tmp_path / 'runs'
    source = examples_dir / EXAMPLE_RUNS_DIR / RUN_ID
    source.mkdir(parents=True)
    (source / MANIFEST_FILE).write_text('{}')
    runs_dir.mkdir()
    assert copy_example_files(examples_dir, runs_dir, [RUN_ID]) == [RUN_ID]
    assert (runs_dir / RUN_ID / MANIFEST_FILE).is_file()
    assert copy_example_files(examples_dir, runs_dir, [RUN_ID]) == []


def test_committed_examples_are_complete() -> None:
    examples = read_examples(settings.EXAMPLES_DIR)
    assert examples.runs
    for run in examples.runs:
        folder = settings.EXAMPLES_DIR / EXAMPLE_RUNS_DIR / run.id
        assert (folder / MANIFEST_FILE).is_file()
        assert run.status != RunStatus.DONE or (folder / FINAL_VIDEO_FILE).is_file()
