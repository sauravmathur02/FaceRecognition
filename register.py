import os
import sqlite3
import cv2
import numpy as np
from insightface.app import FaceAnalysis

app = FaceAnalysis()
app.prepare(ctx_id=0)

person_name = "Saurav"
folder_path = "test_images/Saurav"

embeddings = []

for file in os.listdir(folder_path):

    image_path = os.path.join(folder_path, file)

    image = cv2.imread(image_path)

    if image is None:
        continue

    faces = app.get(image)

    if len(faces) == 0:
        print(f"No face found in {file}")
        continue

    embeddings.append(faces[0].embedding)

if len(embeddings) == 0:
    print("No valid faces found!")
    exit()

embeddings = np.array(embeddings, dtype=np.float32)

# Normalize each embedding
embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

# Compute average
average_embedding = np.mean(embeddings, axis=0)

# Normalize the average embedding
average_embedding = average_embedding / np.linalg.norm(average_embedding)

conn = sqlite3.connect("faces.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM faces WHERE name = ?", (person_name,))

cursor.execute(
    "INSERT INTO faces (name, embedding) VALUES (?, ?)",
    (person_name, average_embedding.astype(np.float32).tobytes())
)

conn.commit()
conn.close()

print("Average embedding stored successfully!")