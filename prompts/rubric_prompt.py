
def get_rubric_prompt(topic, source_material=None):

    reference = source_material or "No reference material provided."

    return f"""
You are an expert subject-matter analyst and educational assessment designer.

Your task is to create a topic-specific evaluation rubric for a
beginner-level educational lesson.

TOPIC:
{topic}

REFERENCE MATERIAL:
{reference}

YOUR TASK:

First, understand the topic and identify its essential learning objectives.

Then create 6 to 8 topic-specific evaluation checkpoints.

CHECKPOINT DESIGN RULES:

1. Every checkpoint must evaluate an important concept or learning
   objective specific to the given topic.

2. Cover the fundamental concepts a beginner must understand.

3. Include important processes, mechanisms, components, or methods
   where they are relevant to the topic.

4. Include applications, use cases, examples, or practical understanding
   where appropriate.

5. Include benefits, limitations, challenges, or comparisons
   where they are relevant.

6. Make checkpoints specific and independently testable.

7. Do not create generic teaching-quality checkpoints such as
   beginner_friendly, logical_flow, or terminology_explanation.
   These are evaluated separately.

8. Do not force a technical workflow onto topics that do not have one.

9. Avoid duplicate or overlapping checkpoints.

10. Do not assume the topic is RAG, AI, or programming.
    Adapt the rubric to the actual topic.

11. Use short snake_case IDs.

12. Every checkpoint must contain:
    - id
    - description
    - expected_evidence

EXPECTED EVIDENCE:
Explain what information or explanation must appear in the lesson
for that checkpoint to pass.

The checkpoints must collectively cover the essential knowledge
needed to understand the topic.

Return only the structured rubric.
"""
