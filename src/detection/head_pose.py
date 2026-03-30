import cv2
import numpy as np
import os


class HeadPoseEstimator:
    """
    Uses OpenCV face landmarks (Facemark LBF) to estimate head direction.
    """

    def __init__(self):
        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        self.facemark = cv2.face.createFacemarkLBF()
        
        # Try to find the model in cv2.data or local models directory
        model_path = None
        
        # 1. Check cv2.data
        if hasattr(cv2, 'data') and hasattr(cv2.data, 'lbfmodel'):
             model_path = cv2.data.lbfmodel
             
        # 2. Check local 'models' directory
        if not model_path:
            # src/detection/head_pose.py -> .../AICheatDetector/models/lbfmodel.yaml
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            local_path = os.path.join(project_root, "models", "lbfmodel.yaml")
            
            if os.path.exists(local_path):
                model_path = local_path
                
        if not model_path:
            raise RuntimeError(
                "Could not find LBF model. "
                "Please ensure 'models/lbfmodel.yaml' exists or 'opencv-contrib-python' is installed correctly."
            )
            
        self.facemark.loadModel(model_path)

    def _calculate_head_direction(self, landmarks):
        """
        landmarks: 68 facial points (x,y)
        Returns: LEFT / RIGHT / DOWN / UP / FORWARD
        """

        # Key landmark indices
        nose = landmarks[30]
        chin = landmarks[8]
        left_eye = landmarks[36]
        right_eye = landmarks[45]

        # Horizontal direction
        horiz_diff = right_eye[0] - left_eye[0]
        horiz_balance = (right_eye[0] + left_eye[0]) / 2 - nose[0]

        # Vertical direction
        vert_diff = chin[1] - nose[1]

        if vert_diff > 35:
            return "DOWN"

        if horiz_balance > 15:
            return "RIGHT"

        if horiz_balance < -15:
            return "LEFT"

        return "FORWARD"

    def estimate(self, frame, person_boxes):
        """
        For each detected person, detect face landmarks and classify head direction.
        Returns:
            [
              { "bbox": (x1,y1,x2,y2), "direction": "LEFT" }
            ]
        """

        results = []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        for box in person_boxes:
            x1, y1, x2, y2 = box["bbox"]
            crop = gray[y1:y2, x1:x2]

            faces = self.face_detector.detectMultiScale(crop, 1.1, 5)

            if len(faces) == 0:
                results.append({"bbox": box["bbox"], "direction": "UNKNOWN"})
                continue

            (fx, fy, fw, fh) = faces[0]

            ok, landmarks = self.facemark.fit(crop, np.array([[(fx, fy, fw, fh)]]))

            if not ok:
                results.append({"bbox": box["bbox"], "direction": "UNKNOWN"})
                continue

            pts = landmarks[0][0]

            # Convert pts from crop to full-frame coords
            pts_full = [(int(x + x1), int(y + y1)) for (x, y) in pts]

            direction = self._calculate_head_direction(pts_full)

            results.append({"bbox": box["bbox"], "direction": direction})

        return results
