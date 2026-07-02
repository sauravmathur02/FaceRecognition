"""
database.py
-----------
One-time initialisation script for the faces database.

Creates the faces table in faces.db if it does not already exist.
Run this once before using the system for the first time. The attendance
database is initialised separately by attendance_db.py.

Usage:
    python database.py

Schema:
    faces(id, name, embedding)
        id        — auto-incremented primary key
        name      — person's display name (used in recognition output)
        embedding — L2-normalized average face embedding stored as BLOB
"""

import sqlite3

from config import DB_NAME

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Create the faces table if it does not already exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS faces (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL,
    embedding BLOB    NOT NULL
)
""")

conn.commit()
conn.close()

print(f"Database '{DB_NAME}' initialised successfully.")