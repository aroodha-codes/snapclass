import dlib
import face_recognition_models
import numpy as np
import streamlit as st
from PIL import Image


FACE_MATCH_THRESHOLD = 0.6



@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()

    predictor = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    encoder = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, predictor, encoder


def get_face_embeddings(image_np):
    """Return one 128-dimensional embedding per detected face."""
    image = Image.fromarray(np.asarray(image_np)).convert("RGB")
    rgb = np.ascontiguousarray(np.asarray(image), dtype=np.uint8)

    detector, predictor, encoder = load_dlib_models()

    # Consistent order for the identification result table.
    faces = sorted(
        detector(rgb, 1),
        key=lambda face: (face.left(), face.top()),
    )

    embeddings = []

    for face in faces:
        landmarks = predictor(rgb, face)
        descriptor = encoder.compute_face_descriptor(
            rgb,
            landmarks,
            1,
        )
        embeddings.append(np.asarray(descriptor, dtype=np.float64))

    return embeddings


@st.cache_resource(ttl=60)
def get_trained_model():
    """Load the enrolled gallery; no classifier training is required."""
    # Lazy import lets the offline evaluation run without Supabase secrets.
    from src.database.db import get_all_students

    embeddings = []
    student_ids = []
    names = {}

    for student in get_all_students() or []:
        stored = student.get("face_embedding")

        if stored is None:
            continue

        vector = np.asarray(stored, dtype=np.float64)

        if vector.shape != (128,) or not np.all(np.isfinite(vector)):
            raise ValueError(
                f"Invalid face embedding for student "
                f"{student.get('student_id')}"
            )

        student_id = student["student_id"]

        embeddings.append(vector)
        student_ids.append(student_id)
        names[student_id] = student.get("name") or str(student_id)

    if not embeddings:
        return None

    return {
        "X": np.vstack(embeddings),
        "y": student_ids,
        "names": names,
    }


def train_classifier():
    """Refresh enrolled faces after registration; preserve existing API."""
    get_trained_model.clear()
    return get_trained_model() is not None


def match_embedding(embedding, gallery, threshold=FACE_MATCH_THRESHOLD):
    """Return accepted identity and nearest distance.

    Rejected faces return (None, distance).
    An empty gallery returns (None, None).
    """
    if not gallery or len(gallery["X"]) == 0:
        return None, None

    distances = np.linalg.norm(
        gallery["X"] - embedding,
        axis=1,
    )

    index = int(np.argmin(distances))
    distance = float(distances[index])

    student_id = (
        gallery["y"][index]
        if distance <= threshold
        else None
    )

    return student_id, distance


def identify_faces(image_np):
    """Return detailed known/unknown results for every detected face."""
    embeddings = get_face_embeddings(image_np)
    gallery = get_trained_model()
    results = []

    for face_number, embedding in enumerate(embeddings, start=1):
        student_id, distance = match_embedding(embedding, gallery)

        results.append({
            "Face": face_number,
            "Student ID": student_id,
            "Name": (
                gallery["names"][student_id]
                if student_id is not None
                else "Unknown"
            ),
            "Status": (
                "Recognized"
                if student_id is not None
                else "Unknown / Not enrolled"
            ),
            "Distance": distance,
        })

    return results


def predict_attendance(class_image_np):
    """Preserve the existing three-value attendance interface."""
    embeddings = get_face_embeddings(class_image_np)
    gallery = get_trained_model()

    detected_students = {}

    for embedding in embeddings:
        student_id, _ = match_embedding(embedding, gallery)

        if student_id is not None:
            detected_students[student_id] = True

    enrolled_ids = (
        list(dict.fromkeys(gallery["y"]))
        if gallery
        else []
    )

    return detected_students, enrolled_ids, len(embeddings)