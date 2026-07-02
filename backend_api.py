"""
backend_api.py
--------------
Thin adapter layer that exposes backend functionality to the Streamlit UI.

Design rules:
    - All recognition logic reuses utils.normalize_embedding and
      utils.cosine_similarity — never reimplemented here.
    - All constants (threshold, DB paths, model name) come from config.py.
    - No business logic lives in the UI — the UI only calls functions in
      this file.
    - This file contains NO Streamlit code.
"""

import os
import glob
import uuid
import sqlite3
from datetime import date, datetime
from typing import Optional

import cv2
import numpy as np

from config import (
    ATTENDANCE_DB,
    CAMERA_ID,
    DB_NAME,
    MODEL_NAME,
    SIMILARITY_THRESHOLD,
    REGISTRATIONS_DIR,
)
from utils import cosine_similarity, get_logger, normalize_embedding

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# InsightFace model — lazy-loaded singleton to avoid reloading on every rerun
# ---------------------------------------------------------------------------
_face_app = None
_embeddings_cache = None



def get_face_app():
    """
    Return the InsightFace FaceAnalysis model, loading it once on first call.
    Subsequent calls return the cached instance immediately.
    """
    global _face_app
    if _face_app is None:
        from insightface.app import FaceAnalysis
        logger.info("Loading InsightFace model '%s' for UI...", MODEL_NAME)
        _face_app = FaceAnalysis(name=MODEL_NAME)
        _face_app.prepare(ctx_id=0, det_size=(320, 320))
        logger.info("InsightFace model ready.")
    return _face_app


# ---------------------------------------------------------------------------
# User / Face database
# ---------------------------------------------------------------------------

def get_all_users() -> list:
    """Return all registered users as a list of (id, name) tuples."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM faces ORDER BY id")
    users = cursor.fetchall()
    conn.close()
    return users


def get_user_count() -> int:
    """Return the total number of registered users (from memory cache)."""
    names, _ = get_all_embeddings()
    return len(names)


def get_all_embeddings() -> tuple:
    """
    Return all stored embeddings as a tuple: (names_list, embeddings_matrix).
    Used by the recognition pipeline — embeddings are cached in memory.
    """
    global _embeddings_cache
    if _embeddings_cache is not None:
        return _embeddings_cache

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, embedding FROM faces")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        _embeddings_cache = ([], np.array([]))
        return _embeddings_cache
        
    names = [r[0] for r in rows]
    embs = np.array([normalize_embedding(np.frombuffer(r[1], dtype=np.float32)) for r in rows])
    
    _embeddings_cache = (names, embs)
    return _embeddings_cache

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, embedding FROM faces")
    rows = cursor.fetchall()
    conn.close()
    
    _embeddings_cache = [
        (name, normalize_embedding(np.frombuffer(blob, dtype=np.float32)))
        for name, blob in rows
    ]
    return _embeddings_cache


def user_exists(name: str) -> bool:
    """Return True if a user with the given name already exists."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM faces WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


import shutil

def delete_user(name: str) -> bool:
    """
    Delete a user from faces.db and their registrations directory.
    Returns True if a record was deleted, False if the user was not found.
    """
    global _embeddings_cache
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faces WHERE name = ?", (name,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    if deleted > 0:
        logger.info("User '%s' deleted via UI.", name)
        _embeddings_cache = None  # Invalidate cache
        user_dir = os.path.join(REGISTRATIONS_DIR, name)
        shutil.rmtree(user_dir, ignore_errors=True)
    return deleted > 0


# ---------------------------------------------------------------------------
# Attendance database
# ---------------------------------------------------------------------------

def is_attendance_marked(name: str, date_str: str) -> bool:
    """Return True if attendance is already recorded for name on date_str."""
    conn = sqlite3.connect(ATTENDANCE_DB)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM attendance WHERE name = ? AND date = ?",
        (name, date_str),
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None


def mark_attendance(name: str) -> tuple:
    """
    Mark attendance for a recognized person (once per calendar day).

    Returns:
        (True, success_message)  — newly recorded.
        (False, info_message)    — already marked today.
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    if is_attendance_marked(name, date_str):
        return False, f"Already marked for {name} today."

    conn = sqlite3.connect(ATTENDANCE_DB)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)",
        (name, date_str, time_str),
    )
    conn.commit()
    conn.close()
    logger.info("Attendance marked for '%s' at %s via UI.", name, time_str)
    return True, f"Attendance marked for {name} at {time_str}"


def get_attendance_records(filter_date: str = None) -> list:
    """
    Return attendance records as list of (id, name, date, time) tuples.
    Optionally filtered by a 'YYYY-MM-DD' date string.
    """
    conn = sqlite3.connect(ATTENDANCE_DB)
    cursor = conn.cursor()
    if filter_date:
        cursor.execute(
            "SELECT id, name, date, time FROM attendance "
            "WHERE date = ? ORDER BY time DESC",
            (filter_date,),
        )
    else:
        cursor.execute(
            "SELECT id, name, date, time FROM attendance "
            "ORDER BY date DESC, time DESC"
        )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_today_attendance() -> list:
    """Return today's attendance records."""
    return get_attendance_records(filter_date=date.today().strftime("%Y-%m-%d"))


def get_today_count() -> int:
    """Return the count of attendance records for today."""
    return len(get_today_attendance())


def clear_all_attendance() -> int:
    """Delete all attendance records. Returns the number of deleted rows."""
    conn = sqlite3.connect(ATTENDANCE_DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance")
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    logger.info("Cleared %d attendance records via UI.", deleted)
    return deleted


def get_dashboard_stats() -> dict:
    """
    Aggregate statistics for the Dashboard page.
    Returns a dict with total_users, today_attendance, recent_records,
    attendance_by_date (last 14 days), and attendance_rate.
    """
    today = date.today().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM faces")
    total_users = cursor.fetchone()[0]
    conn.close()

    conn = sqlite3.connect(ATTENDANCE_DB)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = ?", (today,)
    )
    today_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance")
    total_records = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT date, COUNT(*) AS cnt
        FROM attendance
        GROUP BY date
        ORDER BY date ASC
        LIMIT 14
        """
    )
    attendance_by_date = cursor.fetchall()

    cursor.execute(
        "SELECT name, date, time FROM attendance "
        "ORDER BY date DESC, time DESC LIMIT 10"
    )
    recent_records = cursor.fetchall()

    conn.close()

    return {
        "total_users": total_users,
        "today_attendance": today_count,
        "total_records": total_records,
        "attendance_rate": round(
            (today_count / total_users * 100) if total_users > 0 else 0, 1
        ),
        "attendance_by_date": attendance_by_date,
        "recent_records": recent_records,
    }


# ---------------------------------------------------------------------------
# Face recognition
# ---------------------------------------------------------------------------

def recognize_faces_in_frame(frame: np.ndarray) -> tuple:
    """
    Process a single BGR frame, detect faces, and recognize them.

    Uses:
        - InsightFace (buffalo_l) for detection and embedding extraction.
        - utils.normalize_embedding for L2 normalization.
        - Vectorized dot product for similarity search.
        - SIMILARITY_THRESHOLD from config.py (89%).

    Args:
        frame: BGR NumPy array from OpenCV.

    Returns:
        (annotated_frame, results)
        annotated_frame: Frame with bounding boxes and labels drawn.
        results: List of dicts — name, similarity, bbox, recognized.
    """
    app = get_face_app()
    names_list, embs_matrix = get_all_embeddings()
    detected = app.get(frame)
    results = []

    for face in detected:
        bbox = face.bbox.astype(int)
        query_emb = normalize_embedding(face.embedding.astype(np.float32))

        best_name = "Unknown"
        best_sim = 0.0

        if len(names_list) > 0:
            # Vectorized similarity calculation (dot product since vectors are L2-normalized)
            sims = np.dot(embs_matrix, query_emb) * 100
            best_idx = np.argmax(sims)
            best_sim = sims[best_idx]
            best_name = names_list[best_idx]

        recognized = best_sim >= SIMILARITY_THRESHOLD
        if not recognized:
            best_name = "Unknown"

        results.append({
            "name": best_name,
            "similarity": round(float(best_sim), 2),
            "bbox": bbox.tolist(),
            "recognized": recognized,
        })

        # Draw overlay on frame
        color = (34, 197, 94) if recognized else (239, 68, 68)  # green / red
        label = f"{best_name}  {best_sim:.1f}%"

        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)

        # Label background
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(
            frame,
            (bbox[0], bbox[1] - h - 14),
            (bbox[0] + w + 10, bbox[1]),
            color, -1,
        )
        cv2.putText(
            frame, label,
            (bbox[0] + 5, bbox[1] - 7),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
        )

    return frame, results

# ---------------------------------------------------------------------------
# Camera — persistent VideoCapture singleton so we don’t open/close every frame
# ---------------------------------------------------------------------------
_camera_cap: Optional[cv2.VideoCapture] = None
_camera_available_cache: Optional[bool] = None


def open_camera() -> bool:
    """Open the webcam and keep it open. Returns True on success."""
    global _camera_cap
    if _camera_cap is not None and _camera_cap.isOpened():
        return True
    _camera_cap = cv2.VideoCapture(CAMERA_ID)
    return _camera_cap.isOpened()


def release_camera():
    """Release the webcam."""
    global _camera_cap
    if _camera_cap is not None:
        _camera_cap.release()
        _camera_cap = None


def capture_single_frame() -> Optional[np.ndarray]:
    """
    Grab one frame from the persistent VideoCapture.
    Opens the camera automatically if not already open.
    Returns the frame as a BGR NumPy array, or None on failure.
    """
    global _camera_cap
    if _camera_cap is None or not _camera_cap.isOpened():
        if not open_camera():
            return None
    ret, frame = _camera_cap.read()
    return frame if ret else None


def is_camera_available() -> bool:
    """Return True if the configured camera can be opened. Result is cached."""
    global _camera_cap, _camera_available_cache
    if _camera_cap is not None and _camera_cap.isOpened():
        return True
        
    if _camera_available_cache is not None:
        return _camera_available_cache
        
    cap = cv2.VideoCapture(CAMERA_ID)
    _camera_available_cache = cap.isOpened()
    cap.release()
    return _camera_available_cache


def get_registration_images(person_name: str) -> list:
    user_dir = os.path.join(REGISTRATIONS_DIR, person_name)
    if not os.path.exists(user_dir):
        return []
    return glob.glob(os.path.join(user_dir, "*.jpg")) + glob.glob(os.path.join(user_dir, "*.png"))

def validate_face_image(img_bgr: np.ndarray) -> tuple:
    app = get_face_app()
    faces = app.get(img_bgr)
    if not faces:
        return False, "No face detected.", None
    if len(faces) > 1:
        return False, "Multiple faces detected.", None
    f = faces[0]
    if f.det_score < 0.6:
        return False, f"Confidence too low ({f.det_score:.2f}).", None
    
    area = (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
    if area < 4000:
        return False, "Detected face is too small or blurry.", None
        
    return True, "Valid", f

def update_user_faces(person_name: str, new_images: list, delete_paths: list) -> tuple:
    user_dir = os.path.join(REGISTRATIONS_DIR, person_name)
    os.makedirs(user_dir, exist_ok=True)
    
    valid_faces = []
    for img in new_images:
        is_valid, msg, face_obj = validate_face_image(img)
        if not is_valid:
            return False, f"Image validation failed: {msg}"
        valid_faces.append((img, face_obj))
        
    current_images = get_registration_images(person_name)
    remaining_count = len(current_images) - len(delete_paths) + len(new_images)
    
    if remaining_count < 3:
        return False, f"Cannot update. You must have at least 3 valid registration images. (Currently would have {remaining_count})"
        
    for p in delete_paths:
        if os.path.exists(p) and os.path.dirname(p) == user_dir:
            os.remove(p)
            
    for img, face_obj in valid_faces:
        filename = os.path.join(user_dir, f"{uuid.uuid4().hex}.jpg")
        cv2.imwrite(filename, img)
        
    all_images = get_registration_images(person_name)
    app = get_face_app()
    embeddings = []
    
    for img_path in all_images:
        img_bgr = cv2.imread(img_path)
        if img_bgr is None: continue
        
        faces = app.get(img_bgr)
        if faces:
            valid_f = [f for f in faces if f.det_score >= 0.6]
            if valid_f:
                def _get_area(f):
                    b = f.bbox
                    return (b[2] - b[0]) * (b[3] - b[1])
                largest_face = max(valid_f, key=_get_area)
                emb = normalize_embedding(largest_face.embedding.astype(np.float32))
                embeddings.append(emb)
                
    if not embeddings:
        return False, "Failed to extract embeddings from saved images."
        
    avg_emb = normalize_embedding(np.mean(embeddings, axis=0).astype(np.float32))
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM faces WHERE name = ?", (person_name,))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("UPDATE faces SET embedding = ? WHERE name = ?", (avg_emb.tobytes(), person_name))
        action = "Updated"
    else:
        cursor.execute("INSERT INTO faces (name, embedding) VALUES (?, ?)", (person_name, avg_emb.tobytes()))
        action = "Registered"
        
    conn.commit()
    conn.close()
    
    global _embeddings_cache
    _embeddings_cache = None
    
    logger.info("User '%s' %s via UI from %d images.", person_name, action, len(embeddings))
    return True, f"{action} '{person_name}' successfully using {len(embeddings)} images."

def register_face_from_images(person_name: str, images: list) -> tuple:
    return update_user_faces(person_name, images, [])
