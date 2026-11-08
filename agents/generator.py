
from config import llm
from prompts.generator_prompt import get_generator_prompt


def generate_lesson(
    topic,
    rubric,
    source_material=None,
    previous_lesson=None,
    feedback=None,
    attempt=1
):

    prompt = get_generator_prompt(
        topic=topic,
        rubric=rubric,
        source_material=source_material,
        previous_lesson=previous_lesson,
        feedback=feedback,
        attempt=attempt
    )

    response = llm.invoke(prompt)

    return response.content
