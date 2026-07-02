"""
register_camera.py
------------------
Capture face images from the webcam for a new user registration.

Opens the webcam and displays a live preview. Press 'c' to capture a
photo, 'q' to quit early. Up to 15 images are saved to the folder
test_images/<name>/. Once done, run register.py to generate the
face embedding from these images.

Usage:
    python register_camera.py
"""

import os

import cv2

from config import CAMERA_ID, IMAGE_FOLDER
from utils import get_logger

logger = get_logger(__name__)

person_name = input("Enter person's name: ").strip()
folder = os.path.join(IMAGE_FOLDER, person_name)

os.makedirs(folder, exist_ok=True)
logger.info("Saving images to '%s'.", folder)

cap = cv2.VideoCapture(CAMERA_ID)
count = 0

print("\nLook at the camera. Press 'c' to capture, 'q' to quit.")

try:
    while count < 15:

        ret, frame = cap.read()

        if not ret:
            logger.warning("Failed to read frame from camera.")
            break

        cv2.imshow("Register Face", frame)

        key = cv2.waitKey(1)

        if key == ord("c"):
            filename = os.path.join(folder, f"{count + 1}.jpg")
            cv2.imwrite(filename, frame)
            count += 1
            logger.info("Captured image %d/15 → '%s'", count, filename)
            print(f"Captured {count}/15")

        elif key == ord("q"):
            break

finally:
    # Always release the camera, even if an exception occurs mid-loop
    cap.release()
    cv2.destroyAllWindows()

logger.info("Capture complete. %d image(s) saved to '%s'.", count, folder)
print(f"\n{count} image(s) saved. Now run: python register.py")