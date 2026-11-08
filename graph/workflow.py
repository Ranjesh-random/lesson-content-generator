
from langgraph.graph import StateGraph, START, END

from graph.state import LessonState

from graph.nodes import (
    rubric_designer_node,
    generator_node,
    evaluator_node,
    finalize_node
)

from evaluation.rubric import MAX_RETRIES


def route_after_evaluation(state):

    result = state["evaluation"]["overall_result"]

    if result == "PASS":
        return "finish"

    # MAX_RETRIES = 2 means a maximum of 3 generation attempts.
    if state["attempt_count"] <= MAX_RETRIES:
        return "retry"

    return "finish"


def build_workflow():

    workflow = StateGraph(LessonState)

    workflow.add_node(
        "rubric_designer",
        rubric_designer_node
    )

    workflow.add_node(
        "generator",
        generator_node
    )

    workflow.add_node(
        "evaluator",
        evaluator_node
    )

    workflow.add_node(
        "finalize",
        finalize_node
    )

    workflow.add_edge(
        START,
        "rubric_designer"
    )

    workflow.add_edge(
        "rubric_designer",
        "generator"
    )

    workflow.add_edge(
        "generator",
        "evaluator"
    )

    workflow.add_conditional_edges(
        "evaluator",
        route_after_evaluation,
        {
            "retry": "generator",
            "finish": "finalize"
        }
    )

    workflow.add_edge(
        "finalize",
        END
    )

    return workflow.compile()
