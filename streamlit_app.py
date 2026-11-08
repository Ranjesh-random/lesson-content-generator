
import streamlit as st
import json
from pathlib import Path
from datetime import datetime

from graph.workflow import build_workflow


# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------

st.set_page_config(
    page_title="LessonAI - Self Evaluating Generator",
    page_icon="🎓",
    layout="wide"
)


# ---------------------------------------
# CUSTOM STYLING
# ---------------------------------------

st.markdown("""
<style>
    .main-title {
        font-size: 36px;
        font-weight: 700;
    }

    .subtitle {
        color: #888888;
        font-size: 16px;
    }

    .status-pass {
        padding: 12px;
        border-radius: 8px;
        background-color: #e8f5e9;
        color: #1b5e20;
        font-weight: bold;
    }

    .status-fail {
        padding: 12px;
        border-radius: 8px;
        background-color: #ffebee;
        color: #b71c1c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------
# SESSION STATE
# ---------------------------------------

if "result" not in st.session_state:
    st.session_state.result = None

if "running" not in st.session_state:
    st.session_state.running = False


# ---------------------------------------
# HEADER
# ---------------------------------------

st.markdown(
    '<div class="main-title">🎓 LessonAI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'An autonomous AI system that generates, evaluates, '
    'and improves educational content.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ---------------------------------------
# USER INPUT
# ---------------------------------------

st.subheader("Create Your Lesson")

with st.form("lesson_form"):

    topic = st.text_input(
        "Enter any topic",
        placeholder="e.g. Introduction to RAG, Python, Machine Learning"
    )

    source_material = st.text_area(
        "Reference Material (Optional)",
        placeholder="Paste trusted reference material here...",
        height=150
    )

    st.caption(
        "The system will generate a beginner-friendly lesson "
        "and evaluate it using a dynamically designed rubric."
    )

    generate_button = st.form_submit_button(
        "🚀 Generate & Evaluate Lesson",
        use_container_width=True
    )


# ---------------------------------------
# WORKFLOW EXECUTION
# ---------------------------------------

if generate_button:

    if not topic.strip():
        st.error("Please enter a topic.")
    else:

        st.session_state.result = None

        initial_state = {
            "topic": topic.strip(),
            "source_material": source_material.strip() or None,
            "rubric": {},
            "lesson": "",
            "evaluation": {},
            "feedback": "",
            "attempt_count": 0,
            "rejection_log": [],
            "status": "IN_PROGRESS"
        }

        try:
            with st.status(
                "Running autonomous lesson generation workflow...",
                expanded=True
            ) as status_box:

                st.write("1. Designing topic-specific evaluation rubric")

                workflow = build_workflow()

                st.write("2. Generating beginner-friendly lesson")

                st.write("3. Evaluating lesson against the rubric")

                st.write("4. Regenerating if evaluation fails")

                result = workflow.invoke(initial_state)

                st.write("5. Preparing final submission")

                status_box.update(
                    label="Workflow execution completed",
                    state="complete",
                    expanded=False
                )

            st.session_state.result = result

        except Exception as error:
            st.error(f"Workflow failed: {str(error)}")


# ---------------------------------------
# DISPLAY RESULTS
# ---------------------------------------

if st.session_state.result:

    result = st.session_state.result

    topic = result.get("topic", "")
    lesson = result.get("lesson", "")
    rubric = result.get("rubric", {})
    evaluation = result.get("evaluation", {})
    rejection_log = result.get("rejection_log", [])
    attempt_count = result.get("attempt_count", 0)
    final_status = result.get("status", "UNKNOWN")

    if hasattr(evaluation, "model_dump"):
        evaluation = evaluation.model_dump()

    if hasattr(rubric, "model_dump"):
        rubric = rubric.model_dump()

    if not isinstance(evaluation, dict):
        evaluation = {}

    if not isinstance(rubric, dict):
        rubric = {}

    st.divider()

    st.header("📊 Execution Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Topic", topic)

    with col2:
        st.metric("Generation Attempts", attempt_count)

    with col3:
        st.metric("Final Status", final_status)

    if str(final_status).upper() == "PASS":
        st.success("🎉 Lesson successfully passed evaluation!")
    else:
        st.error(
            "The system terminated without a passing lesson. "
            "Review the evaluation results."
        )

    # -----------------------------------
    # TABS
    # -----------------------------------

    tab1, tab2, tab3, tab4 = st.tabs([
        "📖 Generated Lesson",
        "📋 Evaluation Rubric",
        "🔍 Evaluation Report",
        "🔄 Rejection Log"
    ])

    # -----------------------------------
    # LESSON TAB
    # -----------------------------------

    with tab1:

        st.subheader(f"Introduction to {topic}")

        if lesson:
            st.markdown(lesson)
        else:
            st.warning("No lesson was generated.")

        st.download_button(
            "Download Lesson",
            data=lesson,
            file_name="final_lesson.md",
            mime="text/markdown"
        )

    # -----------------------------------
    # RUBRIC TAB
    # -----------------------------------

    with tab2:

        st.subheader("Topic-Specific Evaluation Rubric")

        st.json(rubric)

        st.download_button(
            "Download Rubric",
            data=json.dumps(
                rubric,
                indent=4,
                ensure_ascii=False,
                default=str
            ),
            file_name="rubric.json",
            mime="application/json"
        )

    # -----------------------------------
    # EVALUATION TAB
    # -----------------------------------

    with tab3:

        st.subheader("Evaluation Results")

        overall_status = evaluation.get(
            "overall_status",
            evaluation.get("status", final_status)
        )

        if str(overall_status).upper() == "PASS":
            st.success("Overall Evaluation: PASS")
        else:
            st.error("Overall Evaluation: FAIL")

        checks = evaluation.get(
            "checks",
            evaluation.get("results", [])
        )

        if isinstance(checks, list):

            passed = 0
            failed = 0

            for check in checks:

                if hasattr(check, "model_dump"):
                    check = check.model_dump()

                check_status = str(
                    check.get("status", "UNKNOWN")
                ).upper()

                if check_status == "PASS":
                    passed += 1
                else:
                    failed += 1

                with st.expander(
                    f"{check.get('check_id', 'Check')} - "
                    f"{check_status}"
                ):

                    st.write("**Reason:**")
                    st.write(check.get("reason", "Not provided"))

                    st.write("**Evidence:**")
                    st.write(check.get("evidence", "Not provided"))

            col1, col2 = st.columns(2)

            col1.metric("Passed Checks", passed)
            col2.metric("Failed Checks", failed)

        st.download_button(
            "Download Evaluation",
            data=json.dumps(
                evaluation,
                indent=4,
                ensure_ascii=False,
                default=str
            ),
            file_name="evaluation.json",
            mime="application/json"
        )

    # -----------------------------------
    # REJECTION LOG TAB
    # -----------------------------------

    with tab4:

        st.subheader("Regeneration History")

        if not rejection_log:

            st.success(
                "No rejected attempts. "
                "The first generated lesson passed evaluation."
            )

        else:

            for index, entry in enumerate(
                rejection_log,
                start=1
            ):

                if hasattr(entry, "model_dump"):
                    entry = entry.model_dump()

                with st.expander(
                    f"Rejected Attempt {entry.get('attempt', index)}"
                ):

                    st.write("**Failed Checks:**")
                    st.write(entry.get("failed_checks", []))

                    st.write("**Reason:**")
                    st.write(entry.get("reason", ""))

                    st.write("**Feedback to Generator:**")
                    st.write(entry.get("feedback", ""))

                    st.write("**Changes in Next Attempt:**")
                    st.write(entry.get("changes", ""))

        st.download_button(
            "Download Rejection Log",
            data=json.dumps(
                rejection_log,
                indent=4,
                ensure_ascii=False,
                default=str
            ),
            file_name="rejection_log.json",
            mime="application/json"
        )

    # -----------------------------------
    # COMPLETE SUBMISSION
    # -----------------------------------

    submission = f"""
# Self-Evaluating Lesson Content Generator

## Topic
{topic}

## Evaluation Rubric
```json
{json.dumps(rubric, indent=4, ensure_ascii=False, default=str)}
```

## Generated Lesson

{lesson}

## Evaluation Report
```json
{json.dumps(evaluation, indent=4, ensure_ascii=False, default=str)}
```

## Rejection Log
```json
{json.dumps(rejection_log, indent=4, ensure_ascii=False, default=str)}
```

## Execution Summary

- Topic: {topic}
- Attempts: {attempt_count}
- Final Status: {final_status}
- Maximum Retries: 2
- Generated At: {datetime.now().isoformat()}
"""

    st.divider()

    st.download_button(
        "📥 Download Complete Submission",
        data=submission,
        file_name="final_submission.md",
        mime="text/markdown",
        use_container_width=True
    )
