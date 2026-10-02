from dataclasses import dataclass

from app.pipeline.agents.caller import StructuredCaller
from app.pipeline.agents.casting import CastingDirector
from app.pipeline.agents.director import Director
from app.pipeline.agents.portrait_judge import PortraitJudge
from app.pipeline.agents.producer import Producer
from app.pipeline.agents.scene_judge import SceneJudge
from app.pipeline.agents.screenwriter import Screenwriter
from app.pipeline.agents.script_critic import ScriptCritic
from app.pipeline.agents.shot_fixer import ShotFixer
from app.providers.protocols import LlmClient


@dataclass(frozen=True)
class Crew:
    producer: Producer
    screenwriter: Screenwriter
    critic: ScriptCritic
    casting: CastingDirector
    portrait_judge: PortraitJudge
    director: Director
    shot_fixer: ShotFixer
    scene_judge: SceneJudge


def build_crew(llm: LlmClient) -> Crew:
    caller = StructuredCaller(llm)
    return Crew(
        producer=Producer(caller),
        screenwriter=Screenwriter(caller),
        critic=ScriptCritic(caller),
        casting=CastingDirector(caller),
        portrait_judge=PortraitJudge(caller),
        director=Director(caller),
        shot_fixer=ShotFixer(caller),
        scene_judge=SceneJudge(caller),
    )
