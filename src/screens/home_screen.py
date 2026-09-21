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
        <section class="sc-hero">
            <div class="sc-hero-label">
                Classroom attendance workspace
            </div>
            <h1>Less time on roll calls.<br>More time for class.</h1>
            <p>
                Register students, identify faces, and keep
                attendance records organised by subject.
            </p>
            <div class="sc-hero-tags">
                <span class="sc-hero-tag">Face identification</span>
                <span class="sc-hero-tag">Subject management</span>
                <span class="sc-hero-tag">Attendance records</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    student_col, teacher_col = st.columns(2, gap="medium")

    with student_col:
        with st.container(
            border=True,
            key="sc_student_portal",
        ):
            st.markdown(
                """
                <div class="sc-portal-symbol" aria-hidden="true">S</div>
                <div class="sc-portal-label">For students</div>
                """,
                unsafe_allow_html=True,
            )

            st.subheader("Your classes. Your attendance.")
            st.write(
                "Create your face profile, join a subject, "
                "and keep track of your attendance."
            )

            if st.button(
                "Open Student Portal",
                type="primary",
                width="stretch",
                key="home_student_portal",
            ):
                st.session_state["login_type"] = "student"
                st.rerun()

    with teacher_col:
        with st.container(
            border=True,
            key="sc_teacher_portal",
        ):
            st.markdown(
                """
                <div class="sc-portal-symbol teacher"
                     aria-hidden="true">T</div>
                <div class="sc-portal-label">For teachers</div>
                """,
                unsafe_allow_html=True,
            )

            st.subheader("A clear view of every class.")
            st.write(
                "Manage your subjects, take attendance, "
                "and review present and absent students."
            )

            if st.button(
                "Open Teacher Portal",
                type="primary",
                width="stretch",
                key="home_teacher_portal",
            ):
                st.session_state["login_type"] = "teacher"
                st.rerun()

    st.space()

    with st.container(
        border=True,
        key="sc_identification_panel",
    ):
        description_col, action_col = st.columns(
            [3, 2],
            vertical_alignment="center",
        )

        with description_col:
            st.subheader("Try face identification")
            st.write(
                "Upload a photo to see a matched name or an Unknown "
                "result, along with the nearest-match distance."
            )
            st.caption("This test does not record attendance.")

        with action_col:
            if st.button(
                "Identify a Face",
                type="secondary",
                key="open_face_identification",
                width="stretch",
            ):
                face_identification_dialog()

    footer_home()