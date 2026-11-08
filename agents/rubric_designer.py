
from pydantic import BaseModel, Field
from config import llm
from prompts.rubric_prompt import get_rubric_prompt
from evaluation.rubric import UNIVERSAL_RUBRIC


class RubricCheckpoint(BaseModel):
    id: str = Field(
        description="Unique checkpoint ID in snake_case"
    )

    description: str = Field(
        description="What this checkpoint evaluates"
    )

    expected_evidence: str = Field(
        description="What evidence must appear in the lesson"
    )


class TopicRubric(BaseModel):
    checkpoints: list[RubricCheckpoint]


def create_rubric(topic, source_material=None):

    structured_llm = llm.with_structured_output(TopicRubric)

    prompt = get_rubric_prompt(
        topic=topic,
        source_material=source_material
    )

    result = structured_llm.invoke(prompt)

    topic_checkpoints = [
        checkpoint.model_dump()
        for checkpoint in result.checkpoints
    ]

    if len(topic_checkpoints) < 4:
        raise ValueError(
            "Rubric Designer generated fewer than 4 topic-specific checkpoints."
        )

    ids = [item["id"] for item in topic_checkpoints]

    if len(ids) != len(set(ids)):
        raise ValueError(
            "Rubric Designer generated duplicate checkpoint IDs."
        )

    # Combine topic-specific and universal checkpoints.
    final_rubric = topic_checkpoints + [
        {
            **item,
            "expected_evidence": item["description"]
        }
        for item in UNIVERSAL_RUBRIC
    ]

    return final_rubric
