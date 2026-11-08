
import json
from pathlib import Path
from datetime import datetime

from graph.workflow import build_workflow


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def to_dict(data):
    """
    Convert Pydantic objects or other supported
    objects into dictionaries.
    """
    if data is None:
        return {}

    if hasattr(data, "model_dump"):
        return data.model_dump()

    if isinstance(data, dict):
        return data

    return data


def save_json(filename, data):
    """Save data as a JSON file."""

    file_path = OUTPUT_DIR / filename

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            to_dict(data),
            file,
            indent=4,
            ensure_ascii=False,
            default=str
        )

    return file_path


def save_markdown(filename, content):
    """Save content as a Markdown file."""

    file_path = OUTPUT_DIR / filename

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content or "")

    return file_path


def format_evaluation(evaluation):
    """
    Format evaluator output for the final report.
    """

    evaluation = to_dict(evaluation)

    if not evaluation:
        return "No evaluation report available."

    lines = []

    overall_status = evaluation.get(
        "overall_status",
        evaluation.get("status", "UNKNOWN")
    )

    lines.append(f"## Overall Result: {overall_status}\n")

    summary = evaluation.get("summary", "")

    if summary:
        lines.append(f"**Summary:** {summary}\n")

    checks = evaluation.get(
        "checks",
        evaluation.get("results", [])
    )

    if isinstance(checks, list):
        for check in checks:
            check = to_dict(check)

            check_id = check.get("check_id", "N/A")
            status = check.get("status", "UNKNOWN")
            reason = check.get("reason", "")
            evidence = check.get("evidence", "")

            lines.append(f"### {check_id}")
            lines.append(f"- **Status:** {status}")
            lines.append(f"- **Reason:** {reason}")

            if evidence:
                lines.append(f"- **Evidence:** {evidence}")

            lines.append("")

    return "\n".join(lines)


def format_rejection_log(rejection_log):
    """Format retry history into readable Markdown."""

    if not rejection_log:
        return (
            "No rejected attempts. "
            "The lesson passed evaluation without regeneration."
        )

    lines = []

    for index, entry in enumerate(rejection_log, start=1):
        entry = to_dict(entry)

        attempt = entry.get("attempt", index)
        failed_checks = entry.get("failed_checks", [])
        reason = entry.get("reason", "")
        feedback = entry.get("feedback", "")
        changes = entry.get("changes", "")

        lines.append(f"### Rejected Attempt {attempt}")

        lines.append(
            f"- **Failed Checks:** {failed_checks}"
        )

        if reason:
            lines.append(f"- **Reason:** {reason}")

        if feedback:
            lines.append(f"- **Feedback Given:** {feedback}")

        if changes:
            lines.append(f"- **Changes in Next Attempt:** {changes}")

        lines.append("")

    return "\n".join(lines)


# --------------------------------------------------
# FINAL SUBMISSION GENERATOR
# --------------------------------------------------

def create_final_submission(state):

    topic = state.get("topic", "Unknown Topic")
    lesson = state.get("lesson", "")
    rubric = state.get("rubric", {})
    evaluation = state.get("evaluation", {})
    rejection_log = state.get("rejection_log", [])

    status = state.get("status", "UNKNOWN")
    attempt_count = state.get("attempt_count", 0)

    evaluation = to_dict(evaluation)
    rubric = to_dict(rubric)

    rejection_report = format_rejection_log(rejection_log)
    evaluation_report = format_evaluation(evaluation)

    final_report = f"""
# Self-Evaluating Lesson Content Generator

## 1. Project Overview

**Topic:** {topic}

**Objective:** Generate a beginner-friendly lesson, evaluate
its quality against a topic-specific rubric, and regenerate
the lesson when it fails evaluation.

## 2. Evaluation Rubric

```json
{json.dumps(rubric, indent=4, ensure_ascii=False, default=str)}
```

## 3. Generated Lesson

{lesson}

## 4. Evaluation Report

{evaluation_report}

## 5. Rejection Log

{rejection_report}

## 6. Execution Summary

- **Topic:** {topic}
- **Total Generation Attempts:** {attempt_count}
- **Final Status:** {status}
- **Maximum Retries:** 2
- **Execution Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""

    return final_report


# --------------------------------------------------
# MAIN APPLICATION
# --------------------------------------------------

def main():

    print("\n" + "=" * 60)
    print("       SELF-EVALUATING LESSON CONTENT GENERATOR")
    print("=" * 60)

    # Step 1: Get topic from user
    topic = input("\nEnter any topic: ").strip()

    if not topic:
        print("\nError: Topic cannot be empty.")
        return

    # Step 2: Optional reference material
    print(
        "\nYou can provide reference material "
        "to improve factual grounding."
    )

    source_material = input(
        "\nEnter reference material (optional): "
    ).strip()

    if not source_material:
        source_material = None

    # Step 3: Initialize LangGraph workflow
    print("\nInitializing workflow...")

    workflow = build_workflow()

    # Step 4: Prepare initial state
    initial_state = {
        "topic": topic,
        "source_material": source_material,
        "rubric": {},
        "lesson": "",
        "evaluation": {},
        "feedback": "",
        "attempt_count": 0,
        "rejection_log": [],
        "status": "IN_PROGRESS"
    }

    # Step 5: Execute workflow
    print("\nStarting lesson generation workflow...\n")

    try:
        final_state = workflow.invoke(initial_state)

    except Exception as error:
        print(f"\nWorkflow execution failed: {error}")
        return

    # Step 6: Extract final outputs
    lesson = final_state.get("lesson", "")
    evaluation = final_state.get("evaluation", {})
    rubric = final_state.get("rubric", {})
    rejection_log = final_state.get("rejection_log", [])

    status = final_state.get("status", "UNKNOWN")
    attempt_count = final_state.get("attempt_count", 0)

    # Step 7: Save individual artifacts
    save_markdown("final_lesson.md", lesson)

    save_json("rubric.json", rubric)

    save_json("evaluation.json", evaluation)

    save_json("rejection_log.json", rejection_log)

    # Step 8: Generate complete submission
    final_submission = create_final_submission(final_state)

    save_markdown(
        "final_submission.md",
        final_submission
    )

    # Step 9: Display final result
    print("\n" + "=" * 60)
    print("                 EXECUTION COMPLETED")
    print("=" * 60)

    print(f"\nTopic: {topic}")
    print(f"Status: {status}")
    print(f"Total Attempts: {attempt_count}")

    print("\nGenerated Files:")

    print("1. outputs/final_lesson.md")
    print("2. outputs/rubric.json")
    print("3. outputs/evaluation.json")
    print("4. outputs/rejection_log.json")
    print("5. outputs/final_submission.md")

    if str(status).upper() == "PASS":
        print("\nSuccess! The lesson passed evaluation.")
    else:
        print(
            "\nThe workflow terminated without "
            "a passing lesson. Check the evaluation report."
        )

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
