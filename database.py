import sqlite3

conn = sqlite3.connect("faces.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS faces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    embedding BLOB NOT NULL
)
""")

conn.commit()

conn.close()

print("Database created successfully.")