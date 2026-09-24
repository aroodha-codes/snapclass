import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import (
    predict_attendance,
    get_face_embeddings,
    get_trained_model,
)
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance, unenroll_student_to_subject
import time

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card

def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {student_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()


    st.space()

    c1, c2 =st.columns(2)
    with c1:
        st.header('Your Enrolled Subjects')
    with c2:
        if st.button('Enroll in Subject', type='primary', width='stretch'):
            enroll_dialog()


    st.divider()


    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0, "attended": 0}

        stats_map[sid]['total'] +=1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1


    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']


        stats = stats_map.get(sid,{"total":0, "attended": 0} )
        def unenroll_button():
            if st.button("Unenroll from tihs course",key=f"unenroll_{student_id}_{sid}",type="tertiary",width="stretch",icon=":material/delete_forever:",):
                unenroll_student_to_subject(student_id, sid)
                st.toast(f'Unenrolled from {sub['name']} successfully!')
                st.rerun()

        with cols[i % 2]:

            subject_card(
                name = sub['name'],
                code =sub['subject_code'],
                section = sub['section'],
                stats = [
                    ('📅', 'Total', stats['total']),
                    ('✅', 'Attended', stats['attended']),
                ],
                footer_callback=unenroll_button
            )
    footer_dashboard()


def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge",
    )

    with c1:
        header_dashboard()

    with c2:
        if st.button(
            "Go back to Home",
            type="secondary",
            key="loginbackbtn",
            shortcut="control+backspace",
        ):
            st.session_state["login_type"] = None
            st.rerun()

    st.header("Login using FaceID", text_alignment="center")
    st.space()
    st.space()

    entry_mode = st.radio(
        "What would you like to do?",
        ["Log in", "Register new profile"],
        horizontal=True,
        key="student_entry_mode",
    )

    show_registration = False
    photo_source = st.camera_input("Position your face in the center")

    if photo_source is not None:
        if entry_mode == "Register new profile":
            # The existing registration code below will check that
            # this photo contains exactly one face before saving it.
            show_registration = True

        else:
            try:
                photo_source.seek(0)
                img = np.array(Image.open(photo_source).convert("RGB"))

                with st.spinner("Scanning your face..."):
                    detected, _, num_faces = predict_attendance(img)

                if num_faces == 0:
                    st.warning("Face not found. Please take another photo.")

                elif num_faces > 1:
                    st.warning(
                        "Multiple faces found. Please take a photo "
                        "containing only your face."
                    )

                elif not detected:
                    st.info(
                        "No registered profile matched this photo. "
                        "Select 'Register new profile' above to create one."
                    )

                else:
                    student_id = next(iter(detected))
                    all_students = get_all_students() or []

                    matched_student = next(
                        (
                            student
                            for student in all_students
                            if student["student_id"] == student_id
                        ),
                        None,
                    )

                    if matched_student is None:
                        st.error(
                            "The matched profile could not be loaded. "
                            "Please try again."
                        )
                    else:
                        st.info(
                            f"Possible match: {matched_student['name']}. "
                            "Continue only if this is your profile."
                        )

                        if st.button(
                            f"Continue as {matched_student['name']}",
                            type="primary",
                            key="confirm_student_login",
                        ):
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = "student"
                            st.session_state.student_data = matched_student
                            st.rerun()

            except Exception:
                st.error(
                    "Could not complete face login. Please check your "
                    "connection and take another photo."
                )
    if show_registration:
        with st.container(border=True):
            st.header("Register new Profile")

            new_name = st.text_input(
                "Enter your name",
                placeholder="E.g. Hamza Rizvi",
            )

            st.subheader("Optional : Voice Enrollment")
            st.info("Register your voice for voice attendance.")

            audio_data = None

            try:
                audio_data = st.audio_input(
                    "Record a short phrase like I am present, "
                    "My name is Akash."
                )
            except Exception:
                st.error(
                    "Audio recording is unavailable. "
                    "You can still register your face."
                )

            if st.button("Create Account", type="primary"):
                clean_name = new_name.strip()

                if not clean_name:
                    st.warning(
                        "Please enter a name, not just spaces."
                    )
                    footer_dashboard()
                    return

                try:
                    photo_source.seek(0)
                    img = np.array(
                        Image.open(photo_source).convert("RGB")
                    )

                    with st.spinner(
                        "Checking your enrollment photo..."
                    ):
                        encodings = get_face_embeddings(img)

                except Exception:
                    st.error(
                        "Could not process your enrollment photo. "
                        "Please take another photo and try again."
                    )
                    footer_dashboard()
                    return

                if len(encodings) != 1:
                    st.warning(
                        "Registration requires exactly one visible "
                        "face. Please take another photo."
                    )
                    footer_dashboard()
                    return

                face_emb = encodings[0].tolist()
                voice_emb = None

                if audio_data is not None:
                    try:
                        voice_emb = get_voice_embedding(
                            audio_data.getvalue()
                        )
                    except Exception:
                        voice_emb = None

                    if voice_emb is None:
                        st.warning(
                            "Voice enrollment failed. Registration "
                            "will continue with your face only."
                        )

                try:
                    with st.spinner("Creating profile..."):
                        response_data = create_student(
                            clean_name,
                            face_embedding=face_emb,
                            voice_embedding=voice_emb,
                        )

                except Exception:
                    st.error(
                        "Registration could not be confirmed. "
                        "The database may have received the request. "
                        "Retake your photo to check whether face "
                        "login recognizes you before attempting "
                        "registration again."
                    )
                    footer_dashboard()
                    return

                if not response_data:
                    st.error(
                        "No profile was returned by the database. "
                        "Retake your photo to check whether "
                        "registration completed before trying again."
                    )
                    footer_dashboard()
                    return

                # Reload enrolled faces on the next recognition.
                get_trained_model.clear()

                st.session_state.is_logged_in = True
                st.session_state.user_role = "student"
                st.session_state.student_data = response_data[0]

                st.toast(f"Profile Created! Hi {clean_name}!")
                time.sleep(1)
                st.rerun()

    footer_dashboard()