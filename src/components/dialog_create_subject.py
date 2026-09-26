import streamlit as st
from src.database.db import create_subject


@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):
    st.write("Enter the details of new subject")

    sub_id = st.text_input(
        "Subject Code",
        placeholder="CS101",
    )
    sub_name = st.text_input(
        "Subject Name",
        placeholder="Introduction to Computer Science",
    )
    sub_section = st.text_input(
        "Section",
        placeholder="A",
    )

    if st.button(
        "Create Subject Now",
        type="primary",
        width="stretch",
    ):
        sub_id = sub_id.strip()
        sub_name = sub_name.strip()
        sub_section = sub_section.strip()

        if not sub_id or not sub_name or not sub_section:
            st.warning(
                "Please enter a subject code, subject name, and section. "
                "Fields cannot contain only spaces."
            )
            return

        try:
            create_subject(
                sub_id,
                sub_name,
                sub_section,
                teacher_id,
            )
            st.toast("Subject Created Succesfully!")
            st.rerun()

        except Exception as e:
            st.error(f"Error: {str(e)}")