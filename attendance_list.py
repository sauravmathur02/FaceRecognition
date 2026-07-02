"""
attendance_list.py
------------------
Standalone script to display all attendance records in a formatted table.

For date-filtered output or to clear records, use attendance.py:
    python attendance.py

Usage:
    python attendance_list.py
"""

import sqlite3

from config import ATTENDANCE_DB

conn = sqlite3.connect(ATTENDANCE_DB)
cursor = conn.cursor()

cursor.execute(
    "SELECT id, name, date, time FROM attendance ORDER BY date, time"
)
rows = cursor.fetchall()

conn.close()

if not rows:
    print("No attendance records found.")
else:
    print("\n" + "=" * 52)
    print(f"  {'ID':<5} {'Name':<20} {'Date':<12} {'Time'}")
    print("-" * 52)

    for row_id, name, date_val, time_val in rows:
        print(f"  {row_id:<5} {name:<20} {date_val:<12} {time_val}")

    print("=" * 52)
    print(f"  Total records: {len(rows)}")