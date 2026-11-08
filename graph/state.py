
from typing import TypedDict


class LessonState(TypedDict):

    topic: str

    source_material: str

    rubric: list

    lesson: str

    evaluation: dict

    feedback: str

    attempt_count: int

    rejection_log: list

    status: str
