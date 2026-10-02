from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.enums import VideoResolution
from app.pipeline.agents import build_crew
from app.pipeline.budget import Budget
from app.pipeline.execution import ExecutionResult, graph_config, interpret_result
from app.pipeline.graph import PipelineContext, PipelineState, build_graph
from app.pipeline.reporting import ConsoleStepReporter
from app.pipeline.storage import RunWorkspace
from tests.fakes import build_fake_providers

TEST_BUDGET_USD = 5.0
TEST_RUN_ID = 'test-run'

type GraphInput = PipelineState | Command[bool] | None


class PipelineHarness:
    def __init__(self, root: Path, flaky_submissions: frozenset[int], failed_submissions: frozenset[int]) -> None:
        self.workspace = RunWorkspace.for_run(root, TEST_RUN_ID)
        self.graph = build_graph().compile(checkpointer=InMemorySaver())
        budget = Budget(TEST_BUDGET_USD)
        providers = build_fake_providers(flaky_submissions=flaky_submissions, failed_submissions=failed_submissions)
        self.providers = providers
        self.context = PipelineContext(
            run_id=TEST_RUN_ID,
            workspace=self.workspace,
            providers=providers,
            crew=build_crew(providers.llm),
            reporter=ConsoleStepReporter(budget),
            budget=budget,
            resolution=VideoResolution.P480,
        )

    async def run(self, idea: str) -> ExecutionResult:
        return await self._invoke(PipelineState(run_id=TEST_RUN_ID, idea=idea))

    async def resume(self, *, approve: bool) -> ExecutionResult:
        return await self._invoke(Command(resume=approve))

    async def continue_run(self) -> ExecutionResult:
        return await self._invoke(None)

    async def state(self) -> PipelineState:
        snapshot = await self.graph.aget_state(graph_config(TEST_RUN_ID))
        return PipelineState.model_validate(snapshot.values)

    async def _invoke(self, graph_input: GraphInput) -> ExecutionResult:
        result: dict[str, Any] = await self.graph.ainvoke(
            graph_input, config=graph_config(TEST_RUN_ID), context=self.context
        )
        return interpret_result(result, self.workspace)


@pytest.fixture
def make_harness(tmp_path: Path) -> Callable[..., PipelineHarness]:
    def factory(
        *, flaky_submissions: frozenset[int] = frozenset(), failed_submissions: frozenset[int] = frozenset()
    ) -> PipelineHarness:
        return PipelineHarness(tmp_path, flaky_submissions, failed_submissions)

    return factory
