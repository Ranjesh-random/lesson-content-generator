
from typing import Literal
from pydantic import BaseModel, Field

from config import llm
from prompts.evaluator_prompt import get_evaluator_prompt


class CheckResult(BaseModel):

    check_id: str = Field(
        description="ID of the evaluation checkpoint"
    )

    status: Literal["PASS", "FAIL"] = Field(
        description="Only PASS or FAIL is allowed"
    )

    reason: str = Field(
        description="Explain why the checkpoint passed or failed"
    )

    evidence: str = Field(
        description="Identify evidence from the generated lesson"
    )


class EvaluationResult(BaseModel):

    checks: list[CheckResult]


def evaluate_lesson(
    topic,
    lesson,
    rubric,
    source_material=None
):

    structured_llm = llm.with_structured_output(
        EvaluationResult
    )

    prompt = get_evaluator_prompt(
        topic=topic,
        lesson=lesson,
        rubric=rubric,
        source_material=source_material
    )

    result = structured_llm.invoke(prompt)

    return result.model_dump()
