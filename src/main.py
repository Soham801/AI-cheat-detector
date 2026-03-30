# src/main.py

import os
import sys

import cv2

# Allow "from detection..." imports when running `python -m src.main` or `python src/main.py`
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# Add 'src' to sys.path so we can import 'detection', 'utils'
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from detection.yolo_detector import YOLODetector
from detection.rules_engine import evaluate_cheating
from utils.drawing import draw_detections, draw_alerts


import json
import time
from pathlib import Path
from utils.email_service import EmailService

# --- Paths -------------------------------------------------------------------
SEAT_CONFIG_PATH = os.path.join(CURRENT_DIR, "config", "seats_config.json")
CAPTURES_DIR = os.path.join(PROJECT_ROOT, "captures")
os.makedirs(CAPTURES_DIR, exist_ok=True)

def load_seat_config():
    if os.path.exists(SEAT_CONFIG_PATH):
        try:
            with open(SEAT_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading seat config: {e}")
            return None
    return None

def main():
    base_dir = PROJECT_ROOT   # root of the project where /models lives
    
    # 1) Setup Email Service
    # No credentials provided -> Simulation Mode (logs to file instead of sending)
    email_service = EmailService()
    
    # 2) Load Seat Config
    seat_config = load_seat_config()
    if seat_config:
        print("Seat configuration loaded.")
    else:
        print("Warning: Seat configuration not found.")

    # 3) Initialize Detector
    detector = YOLODetector(base_dir=base_dir, device="cpu")

    # 4) Start Camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Cannot open camera")
        return

    # Set higher resolution for better accuracy
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("Press 'q' to quit.")

    # Cooldown tracker: student_id -> last_email_time
    email_cooldowns = {}
    COOLDOWN_SECONDS = 10  # 10 seconds

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from camera")
            break

        # Resize to match config if needed, or just use raw frame
        # frame = cv2.resize(frame, (1280, 720))

        detections = detector.detect(frame)
        alerts = evaluate_cheating(detections, seat_config=seat_config)

        # Handle Alerts
        for alert in alerts:
            if alert["severity"] == "high":
                student_info = alert.get("student_info")
                
                # Fallback for unknown students (not in a seat)
                if not student_info:
                    student_info = {
                        "id": "unknown",
                        "student_name": "Unknown",
                        "email": None
                    }
                
                student_id = student_info["id"]
                student_email = student_info.get("email")
                
                # Check cooldown
                last_time = email_cooldowns.get(student_id, 0)
                if time.time() - last_time > COOLDOWN_SECONDS:
                    # Take screenshot
                    timestamp = int(time.time())
                    filename = f"cheat_alert_{student_id}_{timestamp}.jpg"
                    filepath = os.path.join(CAPTURES_DIR, filename)
                    cv2.imwrite(filepath, frame)
                    print(f"[INFO] Screenshot saved: {filepath}")
                    
                    # Send Email
                    subject = f"Cheating Alert: Student {student_info['student_name']}"
                    body = f"Cheating behavior detected: {alert['details']}\n\nSee attached evidence."
                    
                    if student_email:
                        print(f"[ALERT] Sending email to {student_email}...")
                        email_service.send_alert(student_email, subject, body, filepath)
                    else:
                        # Log for unknown student or missing email
                        print(f"[ALERT] Logging alert for {student_info['student_name']} (No email configured)...")
                        email_service.send_alert("LOG_ONLY", subject, body, filepath)
                    
                    email_cooldowns[student_id] = time.time()

        output = frame.copy()
        output = draw_detections(output, detections)
        output = draw_alerts(output, alerts)

        cv2.imshow("AI Cheat Detector", output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
