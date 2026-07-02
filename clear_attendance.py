"""
clear_attendance.py
-------------------
Standalone script to delete all records from the attendance database.

Prompts for confirmation before deleting. To clear attendance from the
main menu, use Option 7 in app.py (which calls this script).
"""

import sqlite3

from config import ATTENDANCE_DB

confirm = input(
    "\nThis will permanently delete ALL attendance records.\n"
    "Type 'yes' to confirm: "
).strip().lower()

if confirm != "yes":
    print("Cancelled. No records were deleted.")
else:
    conn = sqlite3.connect(ATTENDANCE_DB)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM attendance")
    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    print(f"Cleared {deleted} attendance record(s).")