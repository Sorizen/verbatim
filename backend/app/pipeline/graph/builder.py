from typing import Any

from langgraph.graph import END, START, StateGraph

from app.enums import NodeName
from app.pipeline.graph import routing
from app.pipeline.graph.context import PipelineContext
from app.pipeline.graph.nodes import (
    brief_node,
    cast_node,
    finalize_node,
    portrait_check_node,
    portrait_review_node,
    portraits_node,
    rejected_node,
    render_node,
    scene_check_node,
    scene_node,
    script_check_node,
    script_node,
    script_review_node,
    shot_fix_node,
    take_review_node,
)
from app.pipeline.graph.state import PipelineState

type PipelineGraph = StateGraph[PipelineState, PipelineContext, PipelineState, PipelineState]

NODES: dict[NodeName, Any] = {
    NodeName.BRIEF: brief_node,
    NodeName.SCRIPT: script_node,
    NodeName.SCRIPT_CHECK: script_check_node,
    NodeName.SCRIPT_REVIEW: script_review_node,
    NodeName.CAST: cast_node,
    NodeName.PORTRAITS: portraits_node,
    NodeName.PORTRAIT_CHECK: portrait_check_node,
    NodeName.PORTRAIT_REVIEW: portrait_review_node,
    NodeName.SCENE: scene_node,
    NodeName.RENDER: render_node,
    NodeName.SCENE_CHECK: scene_check_node,
    NodeName.SHOT_FIX: shot_fix_node,
    NodeName.FINALIZE: finalize_node,
    NodeName.TAKE_REVIEW: take_review_node,
    NodeName.REJECTED: rejected_node,
}
LINEAR_EDGES = (
    (START, NodeName.BRIEF),
    (NodeName.BRIEF, NodeName.SCRIPT),
    (NodeName.SCRIPT, NodeName.SCRIPT_CHECK),
    (NodeName.CAST, NodeName.PORTRAITS),
    (NodeName.PORTRAITS, NodeName.PORTRAIT_CHECK),
    (NodeName.SCENE, NodeName.RENDER),
    (NodeName.RENDER, NodeName.SCENE_CHECK),
    (NodeName.SHOT_FIX, NodeName.RENDER),
    (NodeName.TAKE_REVIEW, END),
    (NodeName.REJECTED, END),
)


def add_conditional_routes(graph: PipelineGraph) -> None:
    graph.add_conditional_edges(
        NodeName.SCRIPT_CHECK,
        routing.after_script_check,
        [NodeName.CAST, NodeName.SCRIPT, NodeName.SCRIPT_REVIEW],
    )
    graph.add_conditional_edges(NodeName.SCRIPT_REVIEW, routing.after_script_review, [NodeName.CAST, NodeName.REJECTED])
    graph.add_conditional_edges(
        NodeName.PORTRAIT_CHECK,
        routing.after_portrait_check,
        [NodeName.SCENE, NodeName.PORTRAITS, NodeName.PORTRAIT_REVIEW],
    )
    graph.add_conditional_edges(
        NodeName.PORTRAIT_REVIEW, routing.after_portrait_review, [NodeName.SCENE, NodeName.REJECTED]
    )
    graph.add_conditional_edges(
        NodeName.SCENE_CHECK,
        routing.after_scene_check,
        [NodeName.FINALIZE, NodeName.RENDER, NodeName.SHOT_FIX],
    )
    graph.add_conditional_edges(NodeName.FINALIZE, routing.after_finalize, [NodeName.TAKE_REVIEW, END])


def build_graph() -> PipelineGraph:
    graph: PipelineGraph = StateGraph(PipelineState, context_schema=PipelineContext)
    for name, node in NODES.items():
        graph.add_node(name, node)
    for source, target in LINEAR_EDGES:
        graph.add_edge(source, target)
    add_conditional_routes(graph)
    return graph
