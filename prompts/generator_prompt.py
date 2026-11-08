
def get_generator_prompt(
    topic,
    rubric,
    source_material=None,
    previous_lesson=None,
    feedback=None,
    attempt=1
):

    rubric_text = "\n".join([
        f"""
        Checkpoint: {item['id']}
        Description: {item['description']}
        Expected Evidence: {item['expected_evidence']}
        """
        for item in rubric
    ])

    reference = source_material or "No reference material provided."

    if previous_lesson and feedback:

        improvement_instructions = f"""
        This is attempt number {attempt}.

        Your previous lesson failed evaluation.

        PREVIOUS LESSON:
        {previous_lesson}

        EVALUATOR FEEDBACK:
        {feedback}

        Improve the previous lesson using the feedback.

        IMPORTANT:
        - Fix every failed checkpoint.
        - Preserve sections that are already correct.
        - Do not introduce new factual errors.
        - Address the exact problems identified by the evaluator.
        """

    else:

        improvement_instructions = """
        This is the first generation.

        Create a complete, standalone beginner lesson.

        Assume the learner has absolutely no previous knowledge
        of the given topic.
        """

    return f"""
You are an expert educational content creator.

Your task is to create a complete beginner-friendly lesson
on the given topic.

TOPIC:
{topic}

LEARNER LEVEL:
Complete Beginner

REFERENCE MATERIAL:
{reference}

EVALUATION RUBRIC:
{rubric_text}

{improvement_instructions}

LESSON REQUIREMENTS:

1. Introduce the topic and explain its meaning.
2. Explain why the topic is important.
3. Cover all essential concepts identified by the rubric.
4. Explain relevant processes and mechanisms step by step.
5. Explain important terminology.
6. Include practical examples.
7. Explain applications and limitations where relevant.
8. Include a clear summary.

TEACHING RULES:

- Use simple and understandable English.
- Explain every important technical term.
- Do not assume prior knowledge.
- Use relatable examples.
- Explain difficult concepts step by step.
- Avoid unnecessary jargon.
- Maintain technical accuracy.
- Follow a logical teaching sequence.
- Make the lesson standalone.
- Cover every topic-specific checkpoint.

TARGET LENGTH:
Approximately 700-1200 words, adjusted to the complexity
of the topic.

OUTPUT FORMAT:
Return only the complete lesson in Markdown.

Do not include evaluation scores or internal reasoning.
"""
