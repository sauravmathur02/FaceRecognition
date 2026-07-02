"""
attendance_db.py
----------------
One-time initialisation script for the attendance database.

Creates the attendance table in attendance.db if it does not already exist.
Run this once before using the system for the first time.

Usage:
    python attendance_db.py

Schema:
    attendance(id, name, date, time)
        id   — auto-incremented primary key
        name — recognized person's name (matched from faces.db)
        date — attendance date in 'YYYY-MM-DD' format
        time — first recognition timestamp in 'HH:MM:SS' format
"""

import sqlite3

from config import ATTENDANCE_DB

conn = sqlite3.connect(ATTENDANCE_DB)
cursor = conn.cursor()

# Create the attendance table if it does not already exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL,
    date TEXT    NOT NULL,
    time TEXT    NOT NULL
)
""")

conn.commit()
conn.close()

print(f"Database '{ATTENDANCE_DB}' initialised successfully.")