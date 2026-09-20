import streamlit as st

from src.database.db import delete_subject


@st.dialog("Delete Subject")
def delete_subject_dialog(subject_id, subject_name, teacher_id):
    st.write(f"Delete subject: {subject_name}?")

    st.warning(
        "This permanently deletes the subject, all its student enrollments, "
        "and all its attendance records. Student profiles will be kept. "
        "This cannot be undone."
    )

    cancel_col, delete_col = st.columns(2)

    with cancel_col:
        if st.button("Cancel", width="stretch"):
            st.rerun()

    with delete_col:
        if st.button(
            "Yes, Delete Subject",
            type="primary",
            width="stretch",
        ):
            teacher = st.session_state.get("teacher_data", {})

            if (
                not st.session_state.get("is_logged_in")
                or st.session_state.get("user_role") != "teacher"
                or teacher.get("teacher_id") != teacher_id
            ):
                st.error(
                    "Please log in as the teacher who owns this subject."
                )
                return

            try:
                delete_subject(subject_id, teacher_id)
            except Exception:
                st.error(
                    "Could not delete the subject. Check your connection, "
                    "database permissions, and that the subject-delete "
                    "SQL migration has been applied."
                )
                return

            # Discard pending voice results belonging to the deleted subject.
            pending = st.session_state.get("voice_attendance_results")

            if pending and any(
                log.get("subject_id") == subject_id
                for log in pending[1]
            ):
                st.session_state.voice_attendance_results = None

            st.toast("Subject deleted successfully.")
            st.rerun()