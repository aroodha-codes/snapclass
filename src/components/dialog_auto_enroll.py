import time

import streamlit as st

from src.database.db import enroll_student_to_subject
from src.database.config import supabase


@st.dialog("Quick Enrollment")
def auto_enroll_dialog(subject_code):
    student_id = st.session_state.student_data["student_id"]

    try:
        res = (
            supabase.table("subjects")
            .select("subject_id, name")
            .eq("subject_code", subject_code)
            .execute()
        )
    except Exception:
        st.error(
            "Could not check the subject right now. "
            "Please check your connection and reopen the link."
        )

        if st.button("Close"):
            st.query_params.clear()
            st.rerun()

        return

    if not res.data:
        st.error("Subject Code not found!")

        if st.button("Close"):
            st.query_params.clear()
            st.rerun()

        return

    if len(res.data) > 1:
        st.error(
            "This subject code matches more than one subject. "
            "Please ask your teacher for a unique subject code and a new QR link. "
            "You have not been enrolled."
        )

        if st.button("Close"):
            st.query_params.clear()
            st.rerun()

        return

    subject = res.data[0]

    try:
        check = (
            supabase.table("subject_students")
            .select("*")
            .eq("subject_id", subject["subject_id"])
            .eq("student_id", student_id)
            .execute()
        )
    except Exception:
        st.error(
            "Could not check your enrollment right now. "
            "Please check your connection and reopen the link."
        )

        if st.button("Close"):
            st.query_params.clear()
            st.rerun()

        return

    if check.data:
        st.info("Youre already enrolled!")

        if st.button("Got it!"):
            st.query_params.clear()
            st.rerun()

        return

    st.markdown(
        f"Would you like to enroll in **{subject['name']}**?"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("No thanks"):
            st.query_params.clear()
            st.rerun()

    with col2:
        if st.button(
            "Yes enroll now!",
            type="primary",
            width="stretch",
        ):
            try:
                result = enroll_student_to_subject(
                    student_id,
                    subject["subject_id"],
                )
            except Exception:
                st.error(
                    "Enrollment could not be confirmed. "
                    "Check your enrolled subjects before trying again."
                )
                return

            if not result:
                st.warning(
                    "No enrollment confirmation was returned. "
                    "Check your enrolled subjects before trying again."
                )
                return

            st.success("Joined succesfully!")
            st.query_params.clear()
            time.sleep(2)
            st.rerun()