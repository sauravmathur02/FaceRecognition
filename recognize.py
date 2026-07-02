"""
recognize.py
------------
Real-time face recognition and attendance marking via webcam.

Startup behaviour:
    All registered face embeddings are loaded from faces.db into memory
    once, normalized, and cached as a list. This avoids querying the
    database on every video frame (previously ~30 queries/second).

Recognition loop:
    Each webcam frame is scanned for faces using InsightFace. Every
    detected face embedding is compared against the cached embeddings
    using cosine similarity. The best-matching registered person is
    identified. If the similarity meets or exceeds SIMILARITY_THRESHOLD,
    the person is recognized and attendance is marked in attendance.db
    (only once per calendar day).

Press 'q' to quit.
"""

import sqlite3

import cv2
import numpy as np
from insightface.app import FaceAnalysis
from datetime import datetime

from config import (
    ATTENDANCE_DB,
    CAMERA_ID,
    DB_NAME,
    MODEL_NAME,
    SIMILARITY_THRESHOLD,
)
from utils import cosine_similarity, get_logger, normalize_embedding

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Initialise InsightFace model
# ---------------------------------------------------------------------------
logger.info("Loading InsightFace model '%s'...", MODEL_NAME)
app = FaceAnalysis(name=MODEL_NAME)
app.prepare(ctx_id=0)

# ---------------------------------------------------------------------------
# Load all registered face embeddings once at startup.
#
# Previously the database was queried inside the recognition loop on every
# frame (~30 reads/second). Loading and normalizing embeddings here — before
# the loop starts — reduces that to a single query with zero impact on the
# recognition algorithm or accuracy.
# ---------------------------------------------------------------------------
logger.info("Loading registered faces from '%s'...", DB_NAME)

faces_conn = sqlite3.connect(DB_NAME)
faces_cursor = faces_conn.cursor()
faces_cursor.execute("SELECT name, embedding FROM faces")

known_faces = [
    (name, normalize_embedding(np.frombuffer(blob, dtype=np.float32)))
    for name, blob in faces_cursor.fetchall()
]

faces_conn.close()

logger.info("Loaded %d registered face(s). Starting recognition. Press 'q' to quit.", len(known_faces))
print(f"\nLoaded {len(known_faces)} registered face(s). Press 'q' to quit.\n")

# Open the attendance DB — kept open for the duration of the session
attendance_conn = sqlite3.connect(ATTENDANCE_DB)
attendance_cursor = attendance_conn.cursor()

# Open webcam
cap = cv2.VideoCapture(CAMERA_ID)

# ---------------------------------------------------------------------------
# Recognition loop — wrapped in try/finally to guarantee resource cleanup
# even if an unexpected exception occurs mid-loop.
# ---------------------------------------------------------------------------
try:
    while True:
        ret, frame = cap.read()

        if not ret:
            logger.warning("Failed to read frame from camera. Exiting loop.")
            break

        faces = app.get(frame)

        for face in faces:

            box = face.bbox.astype(int)

            # Normalize the detected face embedding
            query_embedding = normalize_embedding(
                face.embedding.astype(np.float32)
            )

            best_name = "Unknown"
            best_similarity = 0.0

            # Compare against every cached registered face
            for name, stored_embedding in known_faces:
                sim = cosine_similarity(query_embedding, stored_embedding) * 100
                if sim > best_similarity:
                    best_similarity = sim
                    best_name = name

            # Threshold decision — algorithm and value are unchanged (89%)
            if best_similarity >= SIMILARITY_THRESHOLD:

                label = f"{best_name} ({best_similarity:.2f}%)"
                color = (0, 255, 0)

                now = datetime.now()
                date_str = now.strftime("%Y-%m-%d")
                time_str = now.strftime("%H:%M:%S")

                # Mark attendance only once per calendar day
                attendance_cursor.execute(
                    """
                    SELECT id FROM attendance
                    WHERE name = ? AND date = ?
                    """,
                    (best_name, date_str),
                )

                if attendance_cursor.fetchone() is None:

                    attendance_cursor.execute(
                        """
                        INSERT INTO attendance (name, date, time)
                        VALUES (?, ?, ?)
                        """,
                        (best_name, date_str, time_str),
                    )
                    attendance_conn.commit()

                    logger.info("Attendance marked: %s at %s", best_name, time_str)
                    print(f"✅ Attendance marked for {best_name} at {time_str}")

            else:
                label = f"Unknown ({best_similarity:.2f}%)"
                color = (0, 0, 255)

            # Draw bounding box around the detected face
            cv2.rectangle(
                frame,
                (box[0], box[1]),
                (box[2], box[3]),
                color,
                2,
            )

            # Draw name and similarity score above the bounding box
            cv2.putText(
                frame,
                label,
                (box[0], box[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2,
            )

        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    # Always release resources, even if an exception occurs
    logger.info("Shutting down. Releasing camera and closing database.")
    cap.release()
    attendance_conn.close()
    cv2.destroyAllWindows()