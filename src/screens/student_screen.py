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
from src.database.db import (
    get_all_students,
    create_student,
    get_student_subjects,
    get_student_attendance,
    unenroll_student_to_subject,
)
import time

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data["student_id"]

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge",
    )

    with c1:
        header_dashboard()

    with c2:
        st.subheader(f"Welcome, {student_data['name']} ")

        if st.button(
            "Logout",
            type="secondary",
            key="loginbackbtn",
            shortcut="control+backspace",
        ):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()

    st.space()

    c1, c2 = st.columns(2)

    with c1:
        st.header("Your Enrolled Subjects")

    with c2:
        if st.button(
            "Enroll in Subject",
            type="primary",
            width="stretch",
        ):
            enroll_dialog()

    st.divider()

    try:
        with st.spinner("Loading your enrolled subjects.."):
            subjects = get_student_subjects(student_id)
            logs = get_student_attendance(student_id)

        if subjects is None or logs is None:
            raise RuntimeError("Student dashboard data is unavailable.")

    except Exception:
        st.error(
            "Could not load your subjects and attendance. "
            "Please check your connection and try again."
        )

        if st.button(
            "Retry",
            key="retry_student_dashboard",
        ):
            st.rerun()

        footer_dashboard()
        return
    stats_map = {}

    for log in logs:
        sid = log["subject_id"]

        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}

        stats_map[sid]["total"] += 1

        if log.get("is_present"):
            stats_map[sid]["attended"] += 1

    cols = st.columns(2)

    for i, sub_node in enumerate(subjects):
        sub = sub_node["subjects"]
        sid = sub["subject_id"]

        stats = stats_map.get(
            sid,
            {"total": 0, "attended": 0},
        )

        def unenroll_button():
            if st.button(
                "Unenroll from tihs course",
                key=f"unenroll_{student_id}_{sid}",
                type="tertiary",
                width="stretch",
                icon=":material/delete_forever:",
            ):
                unenroll_student_to_subject(student_id, sid)
                st.toast(
                    f"Unenrolled from {sub['name']} successfully!"
                )
                st.rerun()

        with cols[i % 2]:
            subject_card(
                name=sub["name"],
                code=sub["subject_code"],
                section=sub["section"],
                stats=[
                    ("📅", "Total", stats["total"]),
                    ("✅", "Attended", stats["attended"]),
                ],
                footer_callback=unenroll_button,
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

    # Temporary stricter login threshold; validate with real test photos.
    login_threshold = 0.5
    show_registration = False

    photo_source = st.camera_input(
        "Position your face in the center",
        key=f"student_camera_{entry_mode}",
    )

    if photo_source is not None:
        if entry_mode == "Register new profile":
            # Check face count before displaying the registration form.
            try:
                photo_source.seek(0)
                registration_image = np.array(
                    Image.open(photo_source).convert("RGB")
                )

                with st.spinner("Checking your registration photo..."):
                    registration_faces = get_face_embeddings(
                        registration_image
                    )

                face_count = len(registration_faces)

                if face_count == 0:
                    st.warning(
                        "No face detected. Please clear the photo and "
                        "take another one with your face clearly visible."
                    )

                elif face_count > 1:
                    st.error(
                        f"{face_count} faces detected. Registration requires "
                        "exactly one face. Please clear the photo and "
                        "take another one with only your face."
                    )

                else:
                    show_registration = True

            except Exception:
                st.error(
                    "Could not process the registration photo. "
                    "Please clear it and take another photo."
                )

        else:
            try:
                photo_source.seek(0)
                img = np.array(
                    Image.open(photo_source).convert("RGB")
                )

                with st.spinner("Scanning your face..."):
                    embeddings = get_face_embeddings(img)

                if len(embeddings) == 0:
                    st.warning(
                        "Face not found. Please take another photo."
                    )

                elif len(embeddings) > 1:
                    st.warning(
                        "Please take a photo containing only your face."
                    )

                else:
                    # Keep each fresh database profile with its embedding.
                    profiles = [
                        student
                        for student in (get_all_students() or [])
                        if student.get("face_embedding") is not None
                    ]

                    if not profiles:
                        st.info(
                            "No registered face profiles are available. "
                            "Select 'Register new profile' above."
                        )

                    else:
                        vectors = []

                        for student in profiles:
                            vector = np.asarray(
                                student["face_embedding"],
                                dtype=np.float64,
                            )

                            if (
                                vector.shape != (128,)
                                or not np.all(np.isfinite(vector))
                            ):
                                raise ValueError(
                                    "A stored face profile is invalid. "
                                    "Its embedding must be checked "
                                    "before login."
                                )

                            vectors.append(vector)

                        query = np.asarray(
                            embeddings[0],
                            dtype=np.float64,
                        )

                        if (
                            query.shape != (128,)
                            or not np.all(np.isfinite(query))
                        ):
                            raise ValueError(
                                "The captured face could not be processed "
                                "correctly. Please take another photo."
                            )

                        distances = np.linalg.norm(
                            np.vstack(vectors) - query,
                            axis=1,
                        )

                        best_index = int(np.argmin(distances))
                        best_distance = float(distances[best_index])
                        matched_student = profiles[best_index]

                        tied = np.count_nonzero(
                            np.isclose(
                                distances,
                                best_distance,
                                rtol=0,
                                atol=1e-8,
                            )
                        ) > 1

                        if tied:
                            st.warning(
                                "Multiple profiles have the same closest "
                                "distance. Login is blocked until the "
                                "profiles are checked."
                            )

                        elif best_distance > login_threshold:
                            st.info(
                                "No sufficiently close face match was found. "
                                "Retake your photo if you already have a "
                                "profile, or select 'Register new profile' "
                                "if you are new."
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

            except ValueError as exc:
                st.error(str(exc))

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

                # Check again before creating a database record.
                try:
                    photo_source.seek(0)
                    img = np.array(
                        Image.open(photo_source).convert("RGB")
                    )

                    with st.spinner("Checking your enrollment photo..."):
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

                # Check fresh database profiles before creating an account.
                try:
                    with st.spinner("Checking for an existing face profile..."):
                        query = np.asarray(
                            encodings[0],
                            dtype=np.float64,
                        )

                        if (
                            query.shape != (128,)
                            or not np.all(np.isfinite(query))
                        ):
                            raise ValueError(
                                "Invalid captured face embedding"
                            )

                        profiles = get_all_students()

                        if profiles is None:
                            raise ValueError(
                                "Student profiles could not be loaded"
                            )

                        duplicate_found = False

                        for student in profiles:
                            stored = np.asarray(
                                student.get("face_embedding"),
                                dtype=np.float64,
                            )

                            if (
                                stored.shape != (128,)
                                or not np.all(np.isfinite(stored))
                            ):
                                raise ValueError(
                                    "Invalid stored face embedding"
                                )

                            distance = float(
                                np.linalg.norm(stored - query)
                            )

                            if distance <= login_threshold:
                                duplicate_found = True

                except Exception:
                    st.error(
                        "Could not safely check existing face profiles. "
                        "No new profile was created. Please retry or ask "
                        "the administrator to check the stored profiles."
                    )
                    footer_dashboard()
                    return

                if duplicate_found:
                    st.warning(
                        "This photo closely matches an existing face profile. "
                        "No new profile was created. If you already registered, "
                        "select 'Log in'. Otherwise, retake your photo or ask "
                        "the administrator to review the match."
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