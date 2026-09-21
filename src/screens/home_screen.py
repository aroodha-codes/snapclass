import streamlit as st

from src.components.header import header_home
from src.components.footer import footer_home
from src.components.dialog_face_identification import (
    face_identification_dialog,
)
from src.ui.base_layout import (
    style_base_layout,
    style_background_home,
)


def home_screen():
    style_background_home()
    style_base_layout()
    header_home()

    st.markdown(
        """
        <div class="sc-home-intro">
            <div class="sc-section-label">Attendance management</div>
            <h1>Your classroom, accounted for.</h1>
            <p>
                Manage subjects, register students, and review
                attendance in one workspace.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    student_col, teacher_col = st.columns(2, gap="large")

    with student_col:
        with st.container(border=True):
            st.subheader("Student Portal")
            st.write(
                "Register your face, join subjects, and check "
                "your attendance."
            )
            st.caption("For students and new registrations")

            if st.button(
                "Open Student Portal",
                type="primary",
                width="stretch",
                key="home_student_portal",
            ):
                st.session_state["login_type"] = "student"
                st.rerun()

    with teacher_col:
        with st.container(border=True):
            st.subheader("Teacher Portal")
            st.write(
                "Manage subjects, take attendance, and review "
                "student records."
            )
            st.caption("For teachers and class administrators")

            if st.button(
                "Open Teacher Portal",
                type="primary",
                width="stretch",
                key="home_teacher_portal",
            ):
                st.session_state["login_type"] = "teacher"
                st.rerun()

    st.divider()

    with st.container(border=True):
        st.subheader("Face Identification")
        st.write(
            "Check a photo against registered face profiles. "
            "View the matched name or an Unknown result."
        )
        st.caption("Identification only — attendance is not recorded.")

        if st.button(
            "Test Face Identification",
            type="secondary",
            key="open_face_identification",
            width="stretch",
        ):
            face_identification_dialog()

    footer_home()