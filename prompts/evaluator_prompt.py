
def get_evaluator_prompt(
    topic,
    lesson,
    rubric,
    source_material=None
):

    rubric_text = "\n".join([
        f"""
        ID: {item['id']}
        Description: {item['description']}
        Expected Evidence: {item['expected_evidence']}
        """
        for item in rubric
    ])

    reference = source_material or (
        "No reference material was supplied. "
        "Evaluate factual accuracy using established subject knowledge, "
        "and do not claim that the lesson is source-verified."
    )

    return f"""
You are a strict educational lesson evaluator.

Evaluate the generated lesson for the following topic:

TOPIC:
{topic}

REFERENCE MATERIAL:
{reference}

GENERATED LESSON:
{lesson}

EVALUATION RUBRIC:
{rubric_text}

STRICT EVALUATION RULES:

1. Evaluate every checkpoint independently.

2. Return exactly one result for every checkpoint ID.

3. Each checkpoint must be marked PASS or FAIL.

4. Do not award partial credit.

5. If important required information is missing, mark FAIL.

6. If the explanation is factually incorrect, mark FAIL.

7. If a checkpoint requires an example, a keyword mention
   without a meaningful example is not sufficient.

8. Evaluate the actual explanation, not merely the presence
   of keywords.

9. Evidence must identify relevant text or sections in the lesson.

10. If there is no supporting evidence, explain that clearly.

11. When reference material is supplied, check consistency
    with that material. Do not invent claims and attribute
    them to the reference.

12. Give specific and actionable reasons for every failure.

13. Do not pass a checkpoint simply because another checkpoint
    covers a similar concept.

Return the structured evaluation.
"""
