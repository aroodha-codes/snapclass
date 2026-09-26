import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from uuid import uuid4
from src.database.db import get_subject_enrollments

from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout,
)
from src.components.dialog_enrolled_students import (
    enrolled_students_dialog,
)
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import (
    check_teacher_exists,
    create_teacher,
    teacher_login,
    get_teacher_subjects,
    get_attendance_for_teacher,
)
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_delete_subject import delete_subject_dialog
from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
from src.database.config import supabase
from src.components.dialog_voice_attendance import voice_attendance_dialog


def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()

    elif (
        "teacher_login_type" not in st.session_state
        or st.session_state.teacher_login_type == "login"
    ):
        teacher_screen_login()

    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()


def teacher_dashboard():
    teacher_data = st.session_state.teacher_data

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge",
    )

    with c1:
        header_dashboard()

    with c2:
        st.subheader(f"Welcome, {teacher_data['name']} ")

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

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"

    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        type1 = (
            "primary"
            if st.session_state.current_teacher_tab == "take_attendance"
            else "tertiary"
        )

        if st.button(
            "Take Attendance",
            type=type1,
            width="stretch",
            icon=":material/ar_on_you:",
        ):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()

    with tab2:
        type2 = (
            "primary"
            if st.session_state.current_teacher_tab == "manage_subjects"
            else "tertiary"
        )

        if st.button(
            "Manage Subjects",
            type=type2,
            width="stretch",
            icon=":material/book_ribbon:",
        ):
            st.session_state.current_teacher_tab = "manage_subjects"
            st.rerun()

    with tab3:
        type3 = (
            "primary"
            if st.session_state.current_teacher_tab == "attendance_records"
            else "tertiary"
        )

        if st.button(
            "Attendance Records",
            type=type3,
            width="stretch",
            icon=":material/cards_stack:",
        ):
            st.session_state.current_teacher_tab = "attendance_records"
            st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()

    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()

    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()

    footer_dashboard()


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data["teacher_id"]

    st.header("Take AI Attendance")

    if "attendance_images" not in st.session_state:
        st.session_state.attendance_images = []

    try:
        subjects = get_teacher_subjects(teacher_id)
    except Exception:
        st.error(
            "Could not load your subjects. "
            "Please check your connection and try again."
        )

        if st.button("Retry", key="retry_attendance_subjects"):
            st.rerun()

        return

    if not subjects:
        with st.container(
            border=True,
            key="sc_empty_subjects",
        ):
            st.markdown(
                '<div class="sc-empty-label">GET STARTED</div>',
                unsafe_allow_html=True,
            )

            st.subheader("Create your first subject")
            st.write(
                "Set up a subject, share its enrollment code with "
                "students, and start recording attendance."
            )

            step1, step2, step3 = st.columns(3, gap="medium")

            with step1:
                st.markdown("**01 · Create a subject**")
                st.caption("Add its name, subject code, and section.")

            with step2:
                st.markdown("**02 · Invite students**")
                st.caption("Share the subject code or enrollment link.")

            with step3:
                st.markdown("**03 · Take attendance**")
                st.caption("Analyze classroom photos and review results.")

            if st.button(
                "Create First Subject",
                type="primary",
                key="create_first_subject",
            ):
                create_subject_dialog(teacher_id)

        return

    subject_options = {
        subject["subject_id"]: (
            f"{subject['name']} - {subject['subject_code']} "
            f"(ID: {subject['subject_id']})"
        )
        for subject in subjects
    }

    col1, col2 = st.columns(
        [3, 1],
        vertical_alignment="bottom",
    )

    with col1:
        selected_subject_id = st.selectbox(
            "Select Subject",
            options=list(subject_options.keys()),
            format_func=lambda subject_id: subject_options[subject_id],
        )
    # Photos belong to this teacher and this subject.
    attendance_context = (teacher_id, selected_subject_id)

    if (
        st.session_state.get("attendance_photo_context")
        != attendance_context
    ):
        st.session_state["attendance_images"] = []
        st.session_state["voice_attendance_results"] = None

        # Prevent previous photo inputs from being reused.
        st.session_state.pop("dialog_cam", None)
        st.session_state.pop("dialog_upload", None)

        st.session_state["attendance_photo_context"] = attendance_context

    with col2:
        if st.button(
            "Add Photos",
            type="primary",
            icon=":material/photo_prints:",
            width="stretch",
        ):
            add_photos_dialog()

    st.divider()

    if st.session_state.attendance_images:
        st.header("Added Photos")
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(
                    img,
                    width="stretch",
                    caption=f"Photo {idx + 1}",
                )

    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button(
            "Clear all photos",
            width="stretch",
            type="tertiary",
            icon=":material/delete:",
            disabled=not has_photos,
        ):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        if st.button(
            "Run Face Analysis",
            width="stretch",
            type="secondary",
            icon=":material/analytics:",
            disabled=not has_photos,
        ):
            with st.spinner("Deep scanning classroom photos..."):
                all_detected_ids = {}
                total_faces = 0

                try:
                    for idx, img in enumerate(
                        st.session_state.attendance_images
                    ):
                        img_np = np.array(img.convert("RGB"))

                        detected, _, num_faces = predict_attendance(
                            img_np
                        )
                        total_faces += num_faces

                        if detected:
                            for sid in detected.keys():
                                student_id = int(sid)

                                all_detected_ids.setdefault(
                                    student_id, []
                                ).append(f"Photo {idx + 1}")

                except Exception:
                    st.error(
                        "Face analysis could not be completed. "
                        "No attendance preview was created or saved. "
                        "Please retry. If this continues, check the "
                        "photos, database connection, and stored face profiles."
                    )
                    return
                # Stop before building attendance if every photo has no faces.
                if total_faces == 0:
                    st.warning(
                        "No faces were detected in the added photos. "
                        "Please add a clearer classroom photo and try again. "
                        "No attendance preview was created or saved."
                    )
                    return

                try:
                    enrolled_students = get_subject_enrollments(
                        selected_subject_id
                    )
                except Exception:
                    st.error(
                        "Could not load the complete enrollment list. "
                        "No attendance preview was created. Please retry. "
                        "If this continues, ask the administrator to "
                        "check for duplicate or invalid enrollments."
                    )
                    return

                if not enrolled_students:
                    st.warning("No students enrolled in this course")
                    return

                results = []
                attendance_to_log = []
                session_id = str(uuid4())

                current_timestamp = datetime.now(timezone.utc).isoformat(
                    timespec="microseconds"
                )

                for node in enrolled_students:
                    student = node["students"]

                    sources = all_detected_ids.get(
                        int(student["student_id"]),
                        [],
                    )
                    is_present = len(sources) > 0

                    results.append(
                        {
                            "Name": student["name"],
                            "ID": student["student_id"],
                            "Source": (
                                ", ".join(sources) if is_present else "-"
                            ),
                            "Status": (
                                "✅ Present" if is_present else "❌ Absent"
                            ),
                        }
                    )

                    attendance_to_log.append(
                        {
                            "session_id": session_id,
                            "student_id": student["student_id"],
                            "subject_id": selected_subject_id,
                            "timestamp": current_timestamp,
                            "is_present": bool(is_present),
                        }
                    )

                attendance_result_dialog(
                    pd.DataFrame(results),
                    attendance_to_log,
                )

    with c3:
        if st.button(
            "Use Voice Attendance",
            type="primary",
            width="stretch",
            icon=":material/mic:",
        ):
            voice_attendance_dialog(selected_subject_id)


def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data["teacher_id"]

    col1, col2 = st.columns(2)

    with col1:
        st.header("Manage Subjects", width="stretch")

    with col2:
        if st.button("Create New Subject", width="stretch"):
            create_subject_dialog(teacher_id)

    try:
        subjects = get_teacher_subjects(teacher_id)
    except Exception:
        st.error(
            "Could not load your subjects and class counts. "
            "Please check your connection and try again."
        )

        if st.button("Retry", key="retry_manage_subjects"):
            st.rerun()

        return

    if not subjects:
        st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE")
        return

    for sub in subjects:
        stats = [
            ("🫂", "Students", sub["total_students"]),
            ("🕰️", "Classes", sub["total_classes"]),
        ]

        subject_card(
            name=sub["name"],
            code=sub["subject_code"],
            section=sub["section"],
            stats=stats,
        )

        if st.button(
            "View Enrolled Students",
            key=f"view_enrolled_{sub['subject_id']}",
            width="stretch",
        ):
            enrolled_students_dialog(
                sub["subject_id"],
                sub["name"],
            )

        if st.button(
            f"Share Code: {sub['name']}",
            key=f"share_{sub['subject_id']}",
            icon=":material/share:",
        ):
            share_subject_dialog(
                sub["name"],
                sub["subject_code"],
            )

        if st.button(
            "Delete Subject",
            key=f"delete_subject_{sub['subject_id']}",
            type="secondary",
        ):
            delete_subject_dialog(
                sub["subject_id"],
                sub["name"],
                teacher_id,
            )

        st.space()


def teacher_tab_attendance_records():
    st.header("Attendance Records")

    teacher_id = st.session_state.teacher_data["teacher_id"]

    try:
        records = get_attendance_for_teacher(teacher_id)
    except Exception:
        st.error("Could not load attendance records. Please try again.")
        return

    if not records:
        st.info("No attendance records found.")
        return

    sessions = {}
    skipped_records = 0

    for record in records:
        subject = record.get("subjects") or {}
        subject_id = record.get("subject_id")
        timestamp = record.get("timestamp")

        # Do not combine records that lack a valid session identifier.
        if subject_id is None or not timestamp:
            skipped_records += 1
            continue

        # Preserve the complete timestamp, including fractional seconds.
        session_id = record.get("session_id")

        if session_id:
            # New records: group by the unique attendance session.
            session_key = (subject_id, "session", session_id)
        else:
            # Historical records do not have a session ID.
            session_key = (subject_id, "legacy", timestamp)
        if session_key not in sessions:
            sessions[session_key] = {
                "timestamp": timestamp,
                "subject_name": subject.get("name") or "Unknown subject",
                "subject_code": subject.get("subject_code") or "-",
                "present": [],
                "absent": [],
            }

        student = record.get("students") or {}
        student_id = record.get("student_id")
        student_name = student.get("name") or (
            f"Unknown student (ID: {student_id})"
        )

        session = sessions[session_key]

        if record.get("is_present"):
            session["present"].append(student_name)
        else:
            session["absent"].append(student_name)

    if skipped_records:
        st.warning(
            f"{skipped_records} attendance record(s) could not be displayed "
            "because their subject ID or session timestamp is missing."
        )

    if not sessions:
        st.info("No valid attendance sessions found.")
        return

    ordered_sessions = sorted(
        sessions.values(),
        key=lambda session: session["timestamp"],
        reverse=True,
    )

    summary_rows = []

    for session in ordered_sessions:
        present_count = len(session["present"])
        total_count = present_count + len(session["absent"])

        summary_rows.append(
            {
                "Time": session["timestamp"],
                "Subject": session["subject_name"],
                "Subject Code": session["subject_code"],
                "Attendance Stats": (
                    f"✅ {present_count} / {total_count} Students"
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(summary_rows),
        width="stretch",
        hide_index=True,
    )

    st.subheader("Session Details")

    for session in ordered_sessions:
        present_count = len(session["present"])
        absent_count = len(session["absent"])
        total_count = present_count + absent_count

        label = (
            f"{session['subject_name']} "
            f"({session['subject_code']}) | "
            f"{session['timestamp']} | "
            f"{present_count} / {total_count} Students"
        )

        with st.expander(label, expanded=False):
            present_col, absent_col = st.columns(2)

            with present_col:
                st.markdown(f"**✅ Present ({present_count})**")

                if session["present"]:
                    for name in sorted(
                        session["present"],
                        key=str.casefold,
                    ):
                        st.text(f"✅ {name}")
                else:
                    st.caption("No students marked present.")

            with absent_col:
                st.markdown(f"**❌ Absent ({absent_count})**")

                if session["absent"]:
                    for name in sorted(
                        session["absent"],
                        key=str.casefold,
                    ):
                        st.text(f"❌ {name}")
                else:
                    st.caption("No students marked absent.")


def login_teacher(username, password):
    username = username.strip()

    if not username or not password:
        return False

    try:
        teacher = teacher_login(username, password)
    except Exception:
        # None distinguishes a service error from invalid credentials.
        return None

    if not teacher:
        return False

    st.session_state.user_role = "teacher"
    st.session_state.teacher_data = teacher
    st.session_state.is_logged_in = True

    return True


def teacher_screen_login():
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

    st.header("Login using password", text_alignment="center")
    st.space()
    st.space()

    teacher_username = st.text_input(
        "Enter username",
        placeholder="ananyaroy",
    )
    teacher_pass = st.text_input(
        "Enter password",
        type="password",
        placeholder="Enter password",
    )

    st.divider()

    btnc1, btnc2 = st.columns(2)
    with btnc1:
        if st.button(
            "Login",
            icon=":material/passkey:",
            shortcut="control+enter",
            width="stretch",
        ):
            login_result = login_teacher(
                teacher_username,
                teacher_pass,
            )

            if login_result is None:
                st.error(
                    "Login is temporarily unavailable. "
                    "Please check your connection and try again."
                )

            elif login_result:
                st.toast("welcome back!", icon="👋")

                import time

                time.sleep(1)
                st.rerun()

            else:
                st.error("Invalid username and password combo")

    with btnc2:
        if st.button(
            "Register Instead",
            type="primary",
            icon=":material/passkey:",
            width="stretch",
        ):
            st.session_state.teacher_login_type = "register"
            st.rerun()

def register_teacher(
    teacher_username,
    teacher_name,
    teacher_pass,
    teacher_pass_confirm,
):
    teacher_username = teacher_username.strip()
    teacher_name = teacher_name.strip()

    if not teacher_username or not teacher_name:
        return False, "Please enter a valid username and name."

    if not teacher_pass or not teacher_pass.strip():
        return False, "Password cannot be empty or contain only spaces."

    if teacher_pass != teacher_pass_confirm:
        return False, "Passwords do not match."

    try:
        if check_teacher_exists(teacher_username):
            return False, "Username already taken."

        create_teacher(
            teacher_username,
            teacher_pass,
            teacher_name,
        )

    except Exception:
        return False, (
            "Registration could not be confirmed. "
            "Please try logging in before attempting registration again."
        )

    return True, "Successfully created! Login now."
def teacher_screen_register():
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

    st.header("Register your teacher profile")
    st.space()
    st.space()

    teacher_username = st.text_input(
        "Enter username",
        placeholder="ananyaroy",
    )
    teacher_name = st.text_input(
        "Enter name",
        placeholder="Ananya Roy",
    )
    teacher_pass = st.text_input(
        "Enter password",
        type="password",
        placeholder="Enter password",
    )
    teacher_pass_confirm = st.text_input(
        "Confirm your password",
        type="password",
        placeholder="Enter password",
    )

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button(
            "Register now",
            icon=":material/passkey:",
            shortcut="control+enter",
            width="stretch",
        ):
            success, message = register_teacher(
                teacher_username,
                teacher_name,
                teacher_pass,
                teacher_pass_confirm,
            )

            if success:
                st.success(message)
                import time

                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)

    with btnc2:
        if st.button(
            "Login Instead",
            type="primary",
            icon=":material/passkey:",
            width="stretch",
        ):
            st.session_state.teacher_login_type = "login"
            st.rerun()
    footer_dashboard()