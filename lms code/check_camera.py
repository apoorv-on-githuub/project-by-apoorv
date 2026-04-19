import sys
import cv2

# Try platform-appropriate backends
if sys.platform == "win32":
    backends = {"DSHOW": cv2.CAP_DSHOW, "MSMF": cv2.CAP_MSMF, "ANY": cv2.CAP_ANY}
elif sys.platform == "darwin":
    backends = {"AVFOUNDATION": cv2.CAP_AVFOUNDATION, "ANY": cv2.CAP_ANY}
else:
    backends = {"V4L2": cv2.CAP_V4L2, "ANY": cv2.CAP_ANY}

for i in range(5):
    for backend_name, backend in backends.items():
        cap = cv2.VideoCapture(i, backend)
        opened = cap.isOpened()
        print(f"Camera {i} | Backend {backend_name}: {'✓ OPEN' if opened else '✗ closed'}")
        cap.release()

