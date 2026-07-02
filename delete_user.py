"""
delete_user.py
--------------
Remove a registered user from the face recognition database.

Prompts for a name, then deletes the matching record from faces.db.
If the name is not found, a clear message is shown and no data is changed.

Usage:
    python delete_user.py
"""

import sqlite3

from config import DB_NAME
from utils import get_logger

logger = get_logger(__name__)

name = input("Enter user name to delete: ").strip()

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("DELETE FROM faces WHERE name = ?", (name,))

if cursor.rowcount > 0:
    logger.info("User '%s' deleted from database.", name)
    print(f"{name} deleted successfully.")
else:
    logger.warning("Delete attempted for unknown user: '%s'.", name)
    print("User not found.")

conn.commit()
conn.close()