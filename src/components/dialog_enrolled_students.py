import pandas as pd
import streamlit as st

from src.database.db import get_subject_students


@st.dialog("Enrolled Students")
def enrolled_students_dialog(subject_id, subject_name):
    teacher = st.session_state.get("teacher_data") or {}
    teacher_id = teacher.get("teacher_id")

    if (
        not st.session_state.get("is_logged_in")
        or st.session_state.get("user_role") != "teacher"
        or teacher_id is None
    ):
        st.error("Please log in as a teacher.")
        return

    st.write(f"Subject: {subject_name}")

    try:
        enrollments = get_subject_students(subject_id, teacher_id)
    except Exception:
        st.error(
            "Could not load enrolled students. "
            "Check your connection and subject access."
        )
        return

    if not enrollments:
        st.info("No students are enrolled in this subject yet.")
        return

    rows = []

    for enrollment in enrollments:
        student = enrollment.get("students") or {}

        rows.append({
            "Student ID": enrollment["student_id"],
            "Name": student.get("name") or "Name unavailable",
        })

    rows.sort(key=lambda row: row["Name"].casefold())

    st.caption(f"Total enrolled students: {len(rows)}")

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        width="stretch",
    )