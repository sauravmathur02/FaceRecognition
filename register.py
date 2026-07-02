"""
register.py
-----------
Register a person's face from images stored in the test_images folder.

For a given person name, reads every image from test_images/<name>/,
extracts a face embedding from each using InsightFace, normalizes and
averages them into a single representative embedding, then saves it to
faces.db.

If the person already exists in the database, the user is prompted to
confirm before the stored embedding is overwritten.

Usage:
    python register.py
"""

import os
import sqlite3

import cv2
import numpy as np
from insightface.app import FaceAnalysis

from config import DB_NAME, IMAGE_FOLDER, MODEL_NAME
from utils import get_logger, normalize_embedding

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Initialise InsightFace model
# ---------------------------------------------------------------------------
app = FaceAnalysis(name=MODEL_NAME)
app.prepare(ctx_id=0)

person_name = input("Enter person's name: ").strip()
folder_path = os.path.join(IMAGE_FOLDER, person_name)

if not os.path.exists(folder_path):
    logger.error("Image folder not found: '%s'", folder_path)
    print("Folder not found!")
    exit()

logger.info("Processing images from '%s'...", folder_path)

embeddings = []

for file in os.listdir(folder_path):

    image_path = os.path.join(folder_path, file)
    image = cv2.imread(image_path)

    if image is None:
        # Not an image file (e.g. .txt, .DS_Store) — skip silently
        continue

    faces = app.get(image)

    if len(faces) == 0:
        logger.warning("No face detected in '%s' — skipping.", file)
        print(f"No face found in {file}")
        continue

    # Normalize each embedding before adding to the list
    embedding = normalize_embedding(faces[0].embedding.astype(np.float32))
    embeddings.append(embedding)

if len(embeddings) == 0:
    logger.error("No valid face embeddings found in '%s'.", folder_path)
    print("No valid face found!")
    exit()

logger.info("Extracted %d valid embedding(s) from '%s'.", len(embeddings), folder_path)

# Average all per-image embeddings, then normalize the result
average_embedding = normalize_embedding(
    np.mean(embeddings, axis=0).astype(np.float32)
)

# ---------------------------------------------------------------------------
# Save to database — update if person exists, insert if new
# ---------------------------------------------------------------------------
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("SELECT id FROM faces WHERE name = ?", (person_name,))
existing = cursor.fetchone()

if existing:

    choice = input(
        f"{person_name} already exists.\nUpdate existing face? (y/n): "
    ).lower()

    if choice != "y":
        logger.info("Registration cancelled by user for '%s'.", person_name)
        print("Registration cancelled.")
        conn.close()
        exit()

    cursor.execute(
        "UPDATE faces SET embedding = ? WHERE name = ?",
        (average_embedding.tobytes(), person_name),
    )

    logger.info("Face embedding updated for '%s'.", person_name)
    print("Face updated successfully!")

else:

    cursor.execute(
        "INSERT INTO faces (name, embedding) VALUES (?, ?)",
        (person_name, average_embedding.tobytes()),
    )

    logger.info("New user '%s' registered successfully.", person_name)
    print("New user registered successfully!")

conn.commit()
conn.close()