from dataclasses import dataclass

from app.enums import VideoResolution
from app.pipeline.agents import Crew
from app.pipeline.budget import Budget
from app.pipeline.reporting import StepReporter
from app.pipeline.storage import RunWorkspace
from app.providers.protocols import Providers


@dataclass(frozen=True)
class PipelineContext:
    run_id: str
    workspace: RunWorkspace
    providers: Providers
    crew: Crew
    reporter: StepReporter
    budget: Budget
    resolution: VideoResolution
