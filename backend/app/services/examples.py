import shutil
from dataclasses import dataclass
from pathlib import Path

import anyio
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository import RunRepository
from app.schema import ExampleRunsFile

EXAMPLE_RUNS_FILE = 'runs.json'
EXAMPLE_RUNS_DIR = 'runs'


@dataclass(frozen=True)
class SeedReport:
    added: list[str]
    copied: list[str]


def read_examples(examples_dir: Path) -> ExampleRunsFile:
    return ExampleRunsFile.model_validate_json((examples_dir / EXAMPLE_RUNS_FILE).read_text())


def copy_example_files(examples_dir: Path, runs_dir: Path, run_ids: list[str]) -> list[str]:
    copied: list[str] = []
    for run_id in run_ids:
        target = runs_dir / run_id
        if target.exists():
            continue
        shutil.copytree(examples_dir / EXAMPLE_RUNS_DIR / run_id, target)
        copied.append(run_id)
    return copied


async def seed_examples(db: AsyncSession, examples_dir: Path, runs_dir: Path) -> SeedReport:
    examples = await anyio.to_thread.run_sync(read_examples, examples_dir)
    repository = RunRepository(db)
    added: list[str] = []
    for snapshot in examples.runs:
        if await repository.get_by_id(snapshot.id):
            continue
        await repository.add_snapshot(snapshot)
        added.append(snapshot.id)
    run_ids = [snapshot.id for snapshot in examples.runs]
    copied = await anyio.to_thread.run_sync(copy_example_files, examples_dir, runs_dir, run_ids)
    return SeedReport(added=added, copied=copied)
