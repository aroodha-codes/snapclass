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
    subjects = []
    last_subject_id = None
    page_size = 500

    # Load all subjects belonging to this teacher.
    while True:
        query = (
            supabase.table("subjects")
            .select("*, subject_students(count)")
            .eq("teacher_id", teacher_id)
            .order("subject_id")
        )

        if last_subject_id is not None:
            query = query.gt("subject_id", last_subject_id)

        response = query.range(0, page_size - 1).execute()
        page = response.data

        if page is None:
            raise RuntimeError("Subjects could not be loaded.")

        if not page:
            break

        subjects.extend(page)
        last_subject_id = page[-1]["subject_id"]

    if not subjects:
        return []

    # Reuse the paginated attendance function from the previous fix.
    attendance_records = get_attendance_for_teacher(teacher_id)

    sessions_by_subject = {
        subject["subject_id"]: set()
        for subject in subjects
    }

    for record in attendance_records:
        subject_id = record.get("subject_id")

        if subject_id not in sessions_by_subject:
            continue

        session_id = record.get("session_id")
        timestamp = record.get("timestamp")

        if session_id:
            sessions_by_subject[subject_id].add(
                ("session", session_id)
            )
        elif timestamp:
            sessions_by_subject[subject_id].add(
                ("legacy", timestamp)
            )

    for subject in subjects:
        enrollment_counts = subject.get("subject_students") or []

        subject["total_students"] = (
            enrollment_counts[0].get("count", 0)
            if enrollment_counts
            else 0
        )

        subject["total_classes"] = len(
            sessions_by_subject[subject["subject_id"]]
        )

        subject.pop("subject_students", None)

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
    records = []
    last_id = None
    page_size = 500

    while True:
        query = (
            supabase.table("attendance_logs")
            .select("*, subjects(*)")
            .eq("student_id", student_id)
            .order("id")
        )

        if last_id is not None:
            query = query.gt("id", last_id)

        response = query.range(0, page_size - 1).execute()
        page = response.data

        if page is None:
            raise RuntimeError("Student attendance could not be loaded.")

        if not page:
            return records

        records.extend(page)
        last_id = page[-1]["id"]

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
    records = []
    last_id = None
    page_size = 500

    while True:
        query = (
            supabase.table("attendance_logs")
            .select("*, subjects!inner(*), students(name)")
            .eq("subjects.teacher_id", teacher_id)
            .order("id")
        )

        if last_id is not None:
            query = query.gt("id", last_id)

        response = query.range(0, page_size - 1).execute()
        page = response.data

        if page is None:
            raise RuntimeError("Attendance records could not be loaded.")

        if not page:
            return records

        records.extend(page)
        last_id = page[-1]["id"]

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
def get_subject_enrollments(
    subject_id,
    columns="*, students(*)",
):
    enrollments = []
    offset = 0
    page_size = 500
    expected_count = None
    seen_students = set()

    while True:
        response = (
            supabase.table("subject_students")
            .select(columns, count="exact")
            .eq("subject_id", subject_id)
            .order("student_id")
            .range(offset, offset + page_size - 1)
            .execute()
        )

        page = response.data
        total = response.count

        if page is None or total is None:
            raise RuntimeError(
                "Enrollment records could not be loaded."
            )

        if expected_count is None:
            expected_count = total
        elif total != expected_count:
            raise RuntimeError(
                "Enrollments changed while loading. Please retry."
            )

        for row in page:
            student_id = row.get("student_id")

            if student_id is None or student_id in seen_students:
                raise RuntimeError(
                    "Duplicate or invalid enrollment records found. "
                    "Please ask the administrator to check this subject."
                )

            seen_students.add(student_id)

        enrollments.extend(page)
        offset += len(page)

        if offset == expected_count:
            return enrollments

        if not page or offset > expected_count:
            raise RuntimeError(
                "Enrollment loading was incomplete. Please retry."
            )
            
def get_subject_students(subject_id, teacher_id):
    # Preserve the existing ownership check.
    subject_response = (
        supabase.table("subjects")
        .select("subject_id")
        .eq("subject_id", subject_id)
        .eq("teacher_id", teacher_id)
        .execute()
    )

    if not subject_response.data:
        raise ValueError("Subject not found or access denied.")

    return get_subject_enrollments(
        subject_id,
        columns="student_id, students(name)",
    )