import time

import streamlit as st

from src.database.config import supabase
from src.database.db import enroll_student_to_subject


@st.dialog("Join a Subject")
def enroll_dialog():
    st.markdown("### Enter your subject code")
    st.caption(
        "Use the code shared by your teacher to join their subject."
    )

    with st.form("subject_enrollment_form"):
        join_code = st.text_input(
            "Subject code",
            placeholder="e.g. CS101",
            help="Enter the code exactly as provided by your teacher.",
        )

        submitted = st.form_submit_button(
            "Find & Join Subject",
            type="primary",
            width="stretch",
        )

    if not submitted:
        return

    join_code = join_code.strip()

    if not join_code:
        st.warning("Please enter a subject code.")
        return

    student = st.session_state.get("student_data") or {}
    student_id = student.get("student_id")

    if (
        not st.session_state.get("is_logged_in")
        or st.session_state.get("user_role") != "student"
        or student_id is None
    ):
        st.error("Please log in as a student before joining a subject.")
        return

    try:
        with st.spinner("Checking subject code..."):
            response = (
                supabase.table("subjects")
                .select("subject_id, name, subject_code, section")
                .eq("subject_code", join_code)
                .execute()
            )

            if not response.data:
                st.error("Subject not found.")
                st.caption(
                    "Check the code, including uppercase and lowercase "
                    "letters, or ask your teacher for the correct code."
                )
                return

            if len(response.data) > 1:
                st.warning(
                    "More than one subject uses this code. "
                    "Please ask your teacher for a unique subject code."
                )
                return

            subject = response.data[0]

            enrollment = (
                supabase.table("subject_students")
                .select("student_id")
                .eq("subject_id", subject["subject_id"])
                .eq("student_id", student_id)
                .execute()
            )

    except Exception:
        st.error(
            "Could not check the subject right now. "
            "Please check your connection and try again."
        )
        return

    with st.container(border=True):
        st.caption("SUBJECT")
        st.write(subject["name"])
        st.caption(
            f"Code: {subject['subject_code']} · "
            f"Section: {subject.get('section') or '—'}"
        )

    if enrollment.data:
        st.info("You are already enrolled in this subject.")
        return

    try:
        with st.spinner("Joining subject..."):
            result = enroll_student_to_subject(
                student_id,
                subject["subject_id"],
            )

    except Exception:
        st.error(
            "Enrollment could not be confirmed. Check your enrolled "
            "subjects before trying again."
        )
        return

    if not result:
        st.warning(
            "No enrollment confirmation was returned. "
            "Check your enrolled subjects before trying again."
        )
        return

    st.success(f"You have joined {subject['name']}.")
    time.sleep(1)
    st.rerun()