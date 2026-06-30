import cv2
from insightface.app import FaceAnalysis

app = FaceAnalysis()
app.prepare(ctx_id=0)

image = cv2.imread("test_images/Saurav_A4_pic.jpg")

faces = app.get(image)

for face in faces:
    box = face.bbox.astype(int)

    cv2.rectangle(
        image,
        (box[0], box[1]),
        (box[2], box[3]),
        (0, 255, 0),
        2,
    )

cv2.imshow("Detected Face", image)
cv2.waitKey(0)
cv2.destroyAllWindows()