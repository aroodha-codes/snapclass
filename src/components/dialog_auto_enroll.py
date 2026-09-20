import streamlit as st

from src.database.db import enroll_student_to_subject
from src.database.config import supabase


def auto_enroll_dialog(subject_code):
    """
    Handles enrollment when a student opens a subject QR/link.

    This is intentionally NOT an st.dialog because the function is
    automatically called from app.py when ?join-code=... is present.
    """

    # Normalize subject code
    subject_code = str(subject_code).strip().upper()

    # Make sure student is logged in
    student_data = st.session_state.get("student_data")

    if not student_data:
        st.warning("Please log in as a student to continue.")
        return

    student_id = student_data["student_id"]

    try:
        # Find subject
        res = (
            supabase
            .table("subjects")
            .select("subject_id, name, subject_code")
            .eq("subject_code", subject_code)
            .execute()
        )

        if not res.data:
            st.error("Subject code not found.")

            if st.button("Close"):
                st.query_params.clear()
                st.rerun()

            return

        subject = res.data[0]

        # Check whether student is already enrolled
        check = (
            supabase
            .table("subject_students")
            .select("*")
            .eq("subject_id", subject["subject_id"])
            .eq("student_id", student_id)
            .execute()
        )

        if check.data:
            st.info(
                f"You are already enrolled in **{subject['name']}**."
            )

            if st.button("Continue"):
                st.query_params.clear()
                st.rerun()

            return

        # Enrollment UI
        with st.container(border=True):
            st.subheader("Quick Enrollment")

            st.markdown(
                f"Would you like to enroll in **{subject['name']}**?"
            )

            st.caption(f"Subject code: {subject_code}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "No thanks",
                    width="stretch"
                ):
                    st.query_params.clear()
                    st.rerun()

            with col2:
                if st.button(
                    "Yes, enroll now",
                    type="primary",
                    width="stretch"
                ):
                    result = enroll_student_to_subject(
                        student_id,
                        subject["subject_id"]
                    )

                    if result:
                        st.success(
                            f"Successfully joined {subject['name']}!"
                        )

                        st.query_params.clear()
                        st.rerun()

                    else:
                        st.error(
                            "Enrollment failed. Please try again."
                        )

    except Exception as e:
        st.error("Unable to complete enrollment.")
        st.exception(e)