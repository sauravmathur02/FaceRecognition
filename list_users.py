"""
list_users.py
-------------
Display all registered users from the face recognition database.

Queries faces.db and prints each user's ID and name in a formatted table,
ordered by registration ID.

Usage:
    python list_users.py
"""

import sqlite3

from config import DB_NAME

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("SELECT id, name FROM faces ORDER BY id")
users = cursor.fetchall()

conn.close()

if not users:
    print("No users found.")
else:
    print("\n" + "=" * 35)
    print(f"  {'ID':<6} {'Name'}")
    print("-" * 35)

    for user_id, name in users:
        print(f"  {user_id:<6} {name}")

    print("=" * 35)
    print(f"  Total: {len(users)} user(s)")