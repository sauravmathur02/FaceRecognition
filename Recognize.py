import sqlite3
import cv2
import numpy as np
from insightface.app import FaceAnalysis

# Load InsightFace model
app = FaceAnalysis()
app.prepare(ctx_id=0)

# Connect to SQLite database
conn = sqlite3.connect("faces.db")
cursor = conn.cursor()

# Open webcam
cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Detect faces
    faces = app.get(frame)

    for face in faces:

        # Bounding box
        box = face.bbox.astype(int)

        # Current face embedding
        query_embedding = face.embedding.astype(np.float32)

        # Normalize query embedding
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        # Read all registered people
        cursor.execute("SELECT name, embedding FROM faces")
        rows = cursor.fetchall()

        best_name = "Unknown"
        best_similarity = 0.0

        for name, embedding_blob in rows:

            stored_embedding = np.frombuffer(
                embedding_blob,
                dtype=np.float32
            )

            # Normalize stored embedding
            stored_embedding = stored_embedding / np.linalg.norm(stored_embedding)

            # Cosine similarity
            similarity = np.dot(query_embedding, stored_embedding)

            similarity_percent = similarity * 100

            if similarity_percent > best_similarity:
                best_similarity = similarity_percent
                best_name = name

        # Apply threshold
        if best_similarity >= 89:
            label = f"{best_name} ({best_similarity:.2f}%)"
            color = (0, 255, 0)
        else:
            label = f"Unknown ({best_similarity:.2f}%)"
            color = (0, 0, 255)

        # Draw bounding box
        cv2.rectangle(
            frame,
            (box[0], box[1]),
            (box[2], box[3]),
            color,
            2
        )

        # Draw label
        cv2.putText(
            frame,
            label,
            (box[0], box[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )

    cv2.imshow("Face Recognition", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
conn.close()
cv2.destroyAllWindows()