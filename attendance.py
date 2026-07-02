"""
attendance.py
-------------
Attendance record utilities for the Face Recognition Attendance System.

Provides two functions:
    show_attendance()   — display all attendance records in a formatted table.
    clear_attendance()  — delete all records after user confirmation.

Can also be run as a standalone script to view today's attendance:
    python attendance.py
"""

import sqlite3
from datetime import date

from config import ATTENDANCE_DB
from utils import get_logger

logger = get_logger(__name__)


def show_attendance(filter_date: str = None) -> None:
    """
    Display attendance records in a formatted table.

    Args:
        filter_date: Optional date string in 'YYYY-MM-DD' format.
                     When provided, only records for that date are shown.
                     When None, all records are displayed.
    """
    conn = sqlite3.connect(ATTENDANCE_DB)
    cursor = conn.cursor()

    if filter_date:
        cursor.execute(
            "SELECT id, name, date, time FROM attendance WHERE date = ? ORDER BY time",
            (filter_date,),
        )
    else:
        cursor.execute(
            "SELECT id, name, date, time FROM attendance ORDER BY date, time"
        )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No attendance records found.")
        return

    print("\n" + "=" * 52)
    print(f"  {'ID':<5} {'Name':<20} {'Date':<12} {'Time'}")
    print("-" * 52)

    for row_id, name, date_val, time_val in rows:
        print(f"  {row_id:<5} {name:<20} {date_val:<12} {time_val}")

    print("=" * 52)
    print(f"  Total records: {len(rows)}")


def clear_attendance() -> None:
    """
    Delete all attendance records after explicit user confirmation.

    Requires the user to type 'yes' (case-insensitive) to proceed.
    Typing anything else cancels the operation without deleting any data.
    """
    confirm = input(
        "\nThis will permanently delete ALL attendance records.\n"
        "Type 'yes' to confirm: "
    ).strip().lower()

    if confirm != "yes":
        print("Cancelled. No records were deleted.")
        logger.info("Clear attendance cancelled by user.")
        return

    conn = sqlite3.connect(ATTENDANCE_DB)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM attendance")
    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    logger.info("Cleared %d attendance record(s).", deleted)
    print(f"Cleared {deleted} attendance record(s).")


if __name__ == "__main__":
    # When run directly: show today's attendance
    today = date.today().strftime("%Y-%m-%d")
    print(f"\nAttendance for today ({today}):")
    show_attendance(filter_date=today)
