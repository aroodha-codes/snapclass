import streamlit as st
import pandas as pd
from datetime import datetime

from src.pipelines.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from src.components.dialog_attendance_results import show_attendance_result


@st.dialog("Voice Attendance")
def voice_attendance_dialog(selected_subject_id):
    st.write(
        "Record audio of students saying I am present. "
        "Then AI will recognize the students"
    )

    # Keep pending results only if every log belongs to this subject.
    pending = st.session_state.get("voice_attendance_results")

    if pending:
        _, pending_logs = pending

        if not pending_logs or any(
            log.get("subject_id") != selected_subject_id
            for log in pending_logs
        ):
            st.session_state.voice_attendance_results = None

    # Separate recording widgets prevent reuse across different subjects.
    audio_data = st.audio_input(
        "Record classroom audio",
        key=f"voice_audio_{selected_subject_id}",
    )

    if st.button(
        "Analyze Audio",
        width="stretch",
        type="primary",
        disabled=audio_data is None,
    ):
        # Defensive check in addition to disabling the button.
        if audio_data is None:
            st.warning("Please record classroom audio first.")
            return

        # getvalue() also works when the same recording is analyzed again.
        audio_bytes = audio_data.getvalue()

        if not audio_bytes:
            st.warning("The recording is empty. Please record again.")
            return

        # A new analysis replaces the previous preview.
        st.session_state.voice_attendance_results = None

        with st.spinner("Processing audio data"):
            enrolled_res = (
                supabase.table("subject_students")
                .select("*, students(*)")
                .eq("subject_id", selected_subject_id)
                .execute()
            )

            enrolled_students = enrolled_res.data or []

            if not enrolled_students:
                st.warning("No students enrolled in this course")
                return

            candidates_dict = {}
            missing_profiles = []

            for node in enrolled_students:
                student = node.get("students")

                if not student or student.get("student_id") is None:
                    st.error(
                        "An enrolled student's profile could not be loaded. "
                        "No attendance results were created. Please retry."
                    )
                    return

                embedding = student.get("voice_embedding")

                if not embedding:
                    missing_profiles.append(
                        f"{student.get('name') or 'Unnamed student'} "
                        f"(ID: {student['student_id']})"
                    )
                else:
                    candidates_dict[student["student_id"]] = embedding

            if missing_profiles:
                st.warning(
                    "Voice attendance requires a registered voice profile "
                    "for every enrolled student. No attendance results "
                    "were created or saved. Use face attendance for this "
                    "session or register the missing voice profiles first."
                )

                st.write("Students without a voice profile:")

                for label in missing_profiles:
                    st.text(label)

                return
            detected_scores = process_bulk_audio(
                audio_bytes,
                candidates_dict,
            )
            if detected_scores is None:
                st.session_state.voice_attendance_results = None
                st.error(
                    "Audio processing failed. No attendance results were "
                    "created or saved. Please record again and retry."
                )
                return

            results = []
            attendance_to_log = []

            current_timestamp = datetime.now().strftime(
                "%Y-%m-%dT%H:%M:%S"
            )

            for node in enrolled_students:
                student = node["students"]
                score = detected_scores.get(
                    student["student_id"],
                    0.0,
                )
                is_present = bool(score > 0)

                results.append({
                    "Name": student["name"],
                    "ID": student["student_id"],
                    "Source": score if is_present else "-",
                    "Status": (
                        "✅ Present" if is_present else "❌ Absent"
                    ),
                })

                attendance_to_log.append({
                    "student_id": student["student_id"],
                    "subject_id": selected_subject_id,
                    "timestamp": current_timestamp,
                    "is_present": is_present,
                })

            st.session_state.voice_attendance_results = (
                pd.DataFrame(results),
                attendance_to_log,
            )

    pending = st.session_state.get("voice_attendance_results")

    if pending:
        df_results, logs = pending

        # Validate again before exposing Confirm & Save.
        if not logs or any(
            log.get("subject_id") != selected_subject_id
            for log in logs
        ):
            st.session_state.voice_attendance_results = None
            return

        st.divider()
        show_attendance_result(df_results, logs)