import asyncio
import sys

from app.config import settings
from app.db import create_engine, create_session_factory
from app.services.examples import seed_examples

REPORT_TEMPLATE = 'examples: {added} added to the database, {copied} copied to {runs_dir}\n'


async def seed() -> None:
    engine = create_engine(pooled=False)
    try:
        async with create_session_factory(engine)() as session:
            report = await seed_examples(session, settings.EXAMPLES_DIR, settings.RUNS_DIR)
            await session.commit()
    finally:
        await engine.dispose()
    sys.stdout.write(
        REPORT_TEMPLATE.format(added=len(report.added), copied=len(report.copied), runs_dir=settings.RUNS_DIR)
    )


if __name__ == '__main__':
    asyncio.run(seed())
