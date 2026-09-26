from src.database.config import supabase
import bcrypt



def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())


def check_teacher_exists(username):
    # Check for unique username, returns false when username is already taken
    response = supabase.table("teachers").select("username").eq("username", username).execute()
    return len(response.data) > 0 



def create_teacher(username, password, name):

    data = { "username" : username, "password": hash_pass(password), "name": name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data


def teacher_login(username, password):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return teacher
    return None


def get_all_students():
    students = []
    last_student_id = None
    page_size = 500

    while True:
        query = (
            supabase.table("students")
            .select("*")
            .order("student_id")
        )

        if last_student_id is not None:
            query = query.gt("student_id", last_student_id)

        response = query.range(0, page_size - 1).execute()
        page = response.data

        if page is None:
            raise RuntimeError("Student profiles could not be loaded.")

        if not page:
            return students

        students.extend(page)
        last_student_id = page[-1]["student_id"]
        
def create_student(new_name, face_embedding=None, voice_embedding=None):
    data = {'name': new_name, 'face_embedding':face_embedding, "voice_embedding": voice_embedding}
    response = supabase.table('students').insert(data).execute()
    return response.data


def create_subject(subject_code, name, section, teacher_id):
    data = {"subject_code": subject_code, "name": name, "section": section, "teacher_id": teacher_id}
    response = supabase.table("subjects").insert(data).execute()
    return response.data

def get_teacher_subjects(teacher_id):
    response = (
        supabase.table("subjects")
        .select(
            "*, subject_students(count), "
            "attendance_logs(session_id, timestamp)"
        )
        .eq("teacher_id", teacher_id)
        .execute()
    )

    subjects = response.data or []

    for sub in subjects:
        enrollment_counts = sub.get("subject_students") or []

        sub["total_students"] = (
            enrollment_counts[0].get("count", 0)
            if enrollment_counts
            else 0
        )

        attendance = sub.get("attendance_logs") or []
        unique_sessions = set()

        for log in attendance:
            session_id = log.get("session_id")
            timestamp = log.get("timestamp")

            if session_id:
                unique_sessions.add(("session", session_id))
            elif timestamp:
                unique_sessions.add(("legacy", timestamp))

        sub["total_classes"] = len(unique_sessions)

        sub.pop("subject_students", None)
        sub.pop("attendance_logs", None)

    return subjects

def  enroll_student_to_subject(student_id, subject_id):
    data = {'student_id': student_id, "subject_id": subject_id}
    response= supabase.table('subject_students').insert(data).execute()
    return response.data


def  unenroll_student_to_subject(student_id, subject_id):
    response= supabase.table('subject_students').delete().eq('student_id', student_id).eq('subject_id', subject_id).execute()
    return response.data



def get_student_subjects(student_id):
    response = supabase.table('subject_students').select('*, subjects(*)').eq('student_id', student_id).execute()
    return response.data


def get_student_attendance(student_id):
    response = supabase.table('attendance_logs').select('*, subjects(*)').eq('student_id', student_id).execute()
    return response.data


def create_attendance(logs):
    if not logs:
        raise ValueError("No attendance records to save.")

    session_id = logs[0].get("session_id")
    subject_id = logs[0].get("subject_id")
    timestamp = logs[0].get("timestamp")

    if not session_id or subject_id is None or not timestamp:
        raise ValueError(
            "Attendance session details are missing. Run analysis again."
        )

    seen_students = set()

    for log in logs:
        student_id = log.get("student_id")

        if (
            log.get("session_id") != session_id
            or log.get("subject_id") != subject_id
            or log.get("timestamp") != timestamp
            or student_id is None
            or student_id in seen_students
            or not isinstance(log.get("is_present"), bool)
        ):
            raise ValueError(
                "Attendance records contain invalid or mixed session data."
            )

        seen_students.add(student_id)

    response = (
        supabase.table("attendance_logs")
        .upsert(
            logs,
            on_conflict="session_id,student_id",
            ignore_duplicates=True,
            default_to_null=False,
        )
        .execute()
    )

    return response.data

def get_attendance_for_teacher(teacher_id):
    response = (
        supabase.table("attendance_logs")
        .select("*, subjects!inner(*), students(name)")
        .eq("subjects.teacher_id", teacher_id)
        .execute()
    )

    return response.data or []

def delete_subject(subject_id, teacher_id):
    """Delete an owned subject and cascade its dependent records.

    Apply the subject-delete SQL migration before using this function.
    """
    if subject_id is None or teacher_id is None:
        raise ValueError("Subject and teacher are required.")

    response = (
        supabase.table("subjects")
        .delete()
        .eq("subject_id", subject_id)
        .eq("teacher_id", teacher_id)
        .execute()
    )

    if not response.data:
        raise ValueError(
            "Subject was not deleted. It may no longer exist "
            "or access was denied."
        )

    return response.data

def get_subject_students(subject_id, teacher_id):
    # Verify that the subject belongs to the current teacher.
    subject_response = (
        supabase.table("subjects")
        .select("subject_id")
        .eq("subject_id", subject_id)
        .eq("teacher_id", teacher_id)
        .execute()
    )

    if not subject_response.data:
        raise ValueError("Subject not found or access denied.")

    response = (
        supabase.table("subject_students")
        .select("student_id, students(name)")
        .eq("subject_id", subject_id)
        .execute()
    )

    return response.data or []