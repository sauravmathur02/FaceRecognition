"""
app.py
------
Main entry point for the Face Recognition Attendance System.

Displays a console menu and dispatches each option by running the
corresponding script as a subprocess. Uses sys.executable to guarantee
that the same Python interpreter (and virtual environment) is used for
every sub-script — regardless of how app.py itself was launched.
"""

import subprocess
import sys


def run(script: str) -> None:
    """
    Run a project script using the current Python interpreter.

    Using sys.executable instead of a bare 'python' string ensures the
    active virtual environment is always used, even on systems where
    'python' resolves to a different installation.

    Args:
        script: Filename of the script to run (e.g. 'register.py').
    """
    subprocess.run([sys.executable, script])


while True:

    print("\n" + "=" * 45)
    print("        FACE RECOGNITION SYSTEM")
    print("=" * 45)

    print("1. Register New Person (Camera)")
    print("2. Generate Face Embedding")
    print("3. Start Face Recognition")
    print("4. Show Registered Users")
    print("5. Delete User")
    print("6. View Attendance")
    print("7. Clear Attendance")
    print("8. Exit")

    choice = input("\nEnter Choice : ")

    if choice == "1":
        run("register_camera.py")

    elif choice == "2":
        run("register.py")

    elif choice == "3":
        run("recognize.py")

    elif choice == "4":
        run("list_users.py")

    elif choice == "5":
        run("delete_user.py")

    elif choice == "6":
        run("attendance_list.py")

    elif choice == "7":
        run("clear_attendance.py")

    elif choice == "8":
        print("\nGoodbye!")
        break

    else:
        print("\nInvalid Choice!")