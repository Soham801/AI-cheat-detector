import cv2
import numpy as np
from typing import Dict, Any, List
from detection.yolo_detector import PersonDetection, ObjectDetection

# --- Colors (BGR) ---
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_ORANGE = (0, 165, 255)
COLOR_CYAN = (255, 255, 0)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_BG_DARK = (30, 30, 30)

def _draw_corner_rect(img, bbox, color, thickness=2, length=20):
    x1, y1, x2, y2 = bbox
    # Top Left
    cv2.line(img, (x1, y1), (x1 + length, y1), color, thickness)
    cv2.line(img, (x1, y1), (x1, y1 + length), color, thickness)
    # Top Right
    cv2.line(img, (x2, y1), (x2 - length, y1), color, thickness)
    cv2.line(img, (x2, y1), (x2, y1 + length), color, thickness)
    # Bottom Left
    cv2.line(img, (x1, y2), (x1 + length, y2), color, thickness)
    cv2.line(img, (x1, y2), (x1, y2 - length), color, thickness)
    # Bottom Right
    cv2.line(img, (x2, y2), (x2 - length, y2), color, thickness)
    cv2.line(img, (x2, y2), (x2, y2 - length), color, thickness)

def draw_detections(frame, detections: Dict[str, Any]):
    persons: List[PersonDetection] = detections.get("Students", [])
    objects: List[ObjectDetection] = detections.get("objects", [])

    # Draw Objects (Phones, etc.)
    for o in objects:
        _draw_corner_rect(frame, o.bbox, COLOR_RED, thickness=2)
        x1, y1, _, _ = o.bbox
        cv2.putText(frame, o.cls_name.upper(), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_RED, 1, cv2.LINE_AA)

    # Draw Persons
    for p in persons:
        _draw_corner_rect(frame, p.bbox, COLOR_CYAN, thickness=2)
        # Keypoints (optional, maybe just eyes/nose)
        # for kp in p.keypoints:
        #     if kp[2] > 0.5:
        #         cv2.circle(frame, (int(kp[0]), int(kp[1])), 3, COLOR_GREEN, -1)

    return frame

def draw_alerts(frame, alerts: List[Dict[str, Any]]):
    h, w = frame.shape[:2]
    
    # --- Sidebar ---
    sidebar_w = 300
    overlay = frame.copy()
    cv2.rectangle(overlay, (w - sidebar_w, 0), (w, h), COLOR_BG_DARK, -1)
    cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
    
    # --- Header Status ---
    status_color = COLOR_GREEN
    status_text = "SYSTEM ACTIVE"
    
    if alerts:
        status_color = COLOR_RED
        status_text = "ALERT DETECTED"
        
        # Draw "REC" indicator
        cv2.circle(frame, (30, 30), 10, COLOR_RED, -1)
        cv2.putText(frame, "REC", (50, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_RED, 2)

    # Top Bar
    cv2.rectangle(frame, (0, 0), (w, 50), COLOR_BLACK, -1)
    cv2.putText(frame, "AI PROCTOR SYSTEM ", (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_WHITE, 2)
    cv2.putText(frame, status_text, (w - sidebar_w + 20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
    
    # --- Alert List in Sidebar ---
    y = 80
    x = w - sidebar_w + 20
    
    cv2.putText(frame, "EVENT LOG:", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_CYAN, 1)
    y += 30
    
    if not alerts:
        cv2.putText(frame, "No active threats", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_GREEN, 1)
    else:
        for alert in alerts:
            # Highlight bounding box of alert
            if "bbox" in alert:
                _draw_corner_rect(frame, alert["bbox"], COLOR_RED, thickness=4)
            
            # Log Text
            color = COLOR_RED if alert["severity"] == "high" else COLOR_ORANGE
            type_str = alert["type"].replace("_", " ").upper()
            cv2.putText(frame, f"> {type_str}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            y += 20
            
            details = alert.get("details", "")
            # Wrap text simply
            if len(details) > 30:
                cv2.putText(frame, details[:30] + "...", (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, COLOR_WHITE, 1)
            else:
                cv2.putText(frame, details, (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, COLOR_WHITE, 1)
            y += 30

    # --- Bottom Info ---
    cv2.putText(frame, "Press 'q' to Exit", (w - sidebar_w + 20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

    return frame
