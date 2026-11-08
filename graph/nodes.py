
from agents.rubric_designer import create_rubric
from agents.generator import generate_lesson
from agents.evaluator import evaluate_lesson

from evaluation.rubric import MAX_RETRIES


def rubric_designer_node(state):

    print("\nCreating Topic-Specific Evaluation Rubric...")

    rubric = create_rubric(
        topic=state["topic"],
        source_material=state.get("source_material")
    )

    print(f"Generated {len(rubric)} checkpoints.")

    return {
        "rubric": rubric,
        "status": "RUBRIC_CREATED"
    }


def generator_node(state):

    attempt = state.get("attempt_count", 0) + 1

    print(f"\nGenerating Lesson - Attempt {attempt}")

    lesson = generate_lesson(
        topic=state["topic"],
        rubric=state["rubric"],
        source_material=state.get("source_material"),
        previous_lesson=state.get("lesson"),
        feedback=state.get("feedback"),
        attempt=attempt
    )

    return {
        "lesson": lesson,
        "attempt_count": attempt,
        "status": "RUNNING"
    }


def evaluator_node(state):

    print("\nEvaluating Generated Lesson...")

    result = evaluate_lesson(
        topic=state["topic"],
        lesson=state["lesson"],
        rubric=state["rubric"],
        source_material=state.get("source_material")
    )

    received_checks = {
        item["check_id"]: item
        for item in result["checks"]
    }

    normalized_checks = []

    for criterion in state["rubric"]:

        check_id = criterion["id"]

        check = received_checks.get(check_id)

        if check is None:

            check = {
                "check_id": check_id,
                "status": "FAIL",
                "reason": "Evaluator did not return this checkpoint.",
                "evidence": "No evaluation evidence provided."
            }

        normalized_checks.append(check)

    all_passed = all(
        item["status"] == "PASS"
        for item in normalized_checks
    )

    evaluation = {
        "checks": normalized_checks,
        "overall_result": "PASS" if all_passed else "FAIL"
    }

    failed_checks = [
        item for item in normalized_checks
        if item["status"] == "FAIL"
    ]

    feedback = ""

    rejection_log = list(
        state.get("rejection_log", [])
    )

    if failed_checks:

        feedback = "\n".join([
            f"""
Checkpoint: {item['check_id']}
Reason: {item['reason']}
Evidence: {item['evidence']}
Required improvement: Fix this issue.
"""
            for item in failed_checks
        ])

        rejection_log.append({
            "attempt": state["attempt_count"],
            "result": "FAIL",
            "failed_checkpoints": failed_checks,
            "improvement_requested": feedback
        })

    return {
        "evaluation": evaluation,
        "feedback": feedback,
        "rejection_log": rejection_log
    }


def finalize_node(state):

    if state["evaluation"]["overall_result"] == "PASS":

        status = "PASSED"

    else:

        status = "FAILED_MAX_RETRIES"

    print(f"\nWorkflow completed: {status}")

    return {
        "status": status
    }
