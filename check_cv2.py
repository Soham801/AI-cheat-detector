
import cv2
import sys

print(f"OpenCV Version: {cv2.__version__}")

try:
    print(f"cv2.face available: {hasattr(cv2, 'face')}")
    if hasattr(cv2, 'face'):
        print("cv2.face is present.")
        try:
            facemark = cv2.face.createFacemarkLBF()
            print("Successfully created FacemarkLBF.")
        except Exception as e:
            print(f"Error creating FacemarkLBF: {e}")
except Exception as e:
    print(f"Error checking cv2.face: {e}")

try:
    print(f"cv2.data available: {hasattr(cv2, 'data')}")
    if hasattr(cv2, 'data'):
        print(f"cv2.data attributes: {dir(cv2.data)}")
        try:
            print(f"cv2.data.lbfmodel: {cv2.data.lbfmodel}")
        except AttributeError:
            print("cv2.data.lbfmodel is NOT present.")
except Exception as e:
    print(f"Error checking cv2.data: {e}")
