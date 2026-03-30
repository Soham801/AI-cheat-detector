# src/detection/rules_engine.py

from typing import Dict, Any, List, Optional
import time
import numpy as np

from detection.yolo_detector import PersonDetection, ObjectDetection

# --- simple in-memory state for "looking too long" ---
_side_look_start_ts: float | None = None
_last_direction: str | None = None

# History for temporal smoothing: student_id -> float (smoothed ratio)
_pose_history: Dict[str, float] = {}


def _compute_head_direction(keypoints: np.ndarray, student_id: str = "unknown", ratio_thresh: float = 0.08) -> str:
    """
    Estimate head direction using nose + eyes from YOLOv8 pose.
    Uses relative distance to be scale-invariant.
    Applies temporal smoothing if student_id is provided.
    """
    global _pose_history
    
    nose = keypoints[0]   # (x, y, conf)
    left_eye = keypoints[1]
    right_eye = keypoints[2]

    if nose[2] < 0.3 or left_eye[2] < 0.3 or right_eye[2] < 0.3:
        return "unknown"

    # Distance between eyes (inter-ocular distance)
    eye_dist = np.linalg.norm(left_eye[:2] - right_eye[:2])
    if eye_dist == 0:
        return "unknown"

    eye_center_x = (left_eye[0] + right_eye[0]) / 2.0
    delta_x = nose[0] - eye_center_x
    
    # Ratio: deviation / eye_width
    current_ratio = delta_x / eye_dist
    
    # Temporal Smoothing (Exponential Moving Average)
    alpha = 0.3 # Smoothing factor (0.0 - 1.0). Lower = smoother but more lag.
    
    prev_ratio = _pose_history.get(student_id, current_ratio)
    smoothed_ratio = alpha * current_ratio + (1 - alpha) * prev_ratio
    _pose_history[student_id] = smoothed_ratio
    
    # Use smoothed ratio for decision
    ratio = smoothed_ratio

    # Lower threshold for higher sensitivity (0.08 is very sensitive)
    if ratio > ratio_thresh:
        return "right"
    elif ratio < -ratio_thresh:
        return "left"
    
    return "forward"


def _get_student_in_seat(person_bbox: List[int], seat_config: Dict[str, Any], frame_width: int, frame_height: int) -> Optional[Dict[str, Any]]:
    """
    Find which seat the person is in.
    Prioritizes the seat that contains the center.
    If no seat contains the center, finds the closest seat.
    """
    if not seat_config:
        return None

    x1, y1, x2, y2 = person_bbox
    cx = (x1 + x2) / 2 / frame_width
    cy = (y1 + y2) / 2 / frame_height
    
    best_seat = None
    min_dist = float("inf")

    for seat in seat_config.get("seats", []):
        # Check if center is inside
        if seat["x1"] <= cx <= seat["x2"] and seat["y1"] <= cy <= seat["y2"]:
            return seat
        
        # Calculate distance to seat center (fallback)
        seat_cx = (seat["x1"] + seat["x2"]) / 2
        seat_cy = (seat["y1"] + seat["y2"]) / 2
        dist = ((cx - seat_cx)**2 + (cy - seat_cy)**2)**0.5
        
        if dist < min_dist:
            min_dist = dist
            best_seat = seat
            
    # Only return best_seat if it's reasonably close (e.g., within 10% of frame width)
    if min_dist < 0.15: 
        return best_seat
        
    return None


def evaluate_cheating(
    detections: Dict[str, Any],
    seat_config: Optional[Dict[str, Any]] = None,
    side_look_seconds: float = 0.5, # Tightened from 2.0s to 0.5s
) -> List[Dict[str, Any]]:
    """
    Core rules engine.
    """
    global _side_look_start_ts, _last_direction

    persons: List[PersonDetection] = detections.get("persons", [])
    objects: List[ObjectDetection] = detections.get("objects", [])
    frame_size = detections.get("frame_size", (1280, 720)) # w, h

    now = time.time()
    alerts: List[Dict[str, Any]] = []

    # Helper to find student info for a given person detection
    def get_info(p):
        return _get_student_in_seat(p.bbox, seat_config, frame_size[0], frame_size[1])

    # ---------- Rule 1: Phone or Chit (Book) near any student ----------
    prohibited_items = [o for o in objects if o.cls_name in ("phone", "book")]
    for p in persons:
        for item in prohibited_items:
            if _iou(p.bbox, item.bbox) > 0.1:
                student_info = get_info(p)
                
                item_type = "Phone" if item.cls_name == "phone" else "Suspicious Material (Chit/Book)"
                alert_type = "phone_near_student" if item.cls_name == "phone" else "suspicious_material"
                
                alerts.append({
                    "type": alert_type,
                    "severity": "high",
                    "details": f"{item_type} detected near student.",
                    "student_info": student_info,
                    "bbox": p.bbox
                })
                break 

    # ---------- Rule 2: looking left/right for too long ----------
    looking_student = None
    current_direction = "forward"

    for p in persons:
        s_info = get_info(p)
        s_id = s_info["id"] if s_info else "unknown"
        
        # Use lower threshold for better sensitivity (0.08) + smoothing
        direction = _compute_head_direction(p.keypoints, student_id=s_id, ratio_thresh=0.08)
        
        if direction in ("left", "right"):
            current_direction = direction
            looking_student = p
            break

    if current_direction in ("left", "right") and looking_student:
        if _last_direction != current_direction:
            _side_look_start_ts = now
            _last_direction = current_direction
        else:
            if _side_look_start_ts is None:
                _side_look_start_ts = now
            elapsed = now - _side_look_start_ts
            if elapsed >= side_look_seconds:
                student_info = get_info(looking_student)
                alerts.append({
                    "type": "looking_side_too_long",
                    "severity": "high",
                    "details": f"Student looking {current_direction} for {elapsed:.1f}s.",
                    "student_info": student_info,
                    "bbox": looking_student.bbox
                })
    else:
        _side_look_start_ts = None
        _last_direction = None

    # ---------- Rule 3: Multiple people in one seat ----------
    if seat_config:
        # Count people per seat
        seat_counts = {seat["id"]: [] for seat in seat_config["seats"]}
        for p in persons:
            s = get_info(p)
            if s:
                seat_counts[s["id"]].append(p)
        
        for seat_id, people_in_seat in seat_counts.items():
            # Multiple people
            if len(people_in_seat) > 1:
                # Find the seat info object
                seat_info = next(s for s in seat_config["seats"] if s["id"] == seat_id)
                alerts.append({
                    "type": "multiple_people_in_seat",
                    "severity": "high",
                    "details": f"Multiple people detected in seat {seat_id}.",
                    "student_info": seat_info,
                    "bbox": people_in_seat[0].bbox # Just use first person's bbox
                })
            
            # Absence (Optional - maybe low severity or just log)
            elif len(people_in_seat) == 0:
                 # seat_info = next(s for s in seat_config["seats"] if s["id"] == seat_id)
                 pass

    # ---------- Rule 4: Students too close (Proximity) ----------
    # Check distance between every pair of students
    # Threshold: e.g., 25% of frame width (Increased from 15%)
    proximity_thresh_px = frame_size[0] * 0.25
    
    for i in range(len(persons)):
        for j in range(i + 1, len(persons)):
            p1 = persons[i]
            p2 = persons[j]
            
            # Centroids
            c1 = ((p1.bbox[0] + p1.bbox[2]) / 2, (p1.bbox[1] + p1.bbox[3]) / 2)
            c2 = ((p2.bbox[0] + p2.bbox[2]) / 2, (p2.bbox[1] + p2.bbox[3]) / 2)
            
            dist = ((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)**0.5
            
            if dist < proximity_thresh_px:
                student_info_1 = get_info(p1)
                student_info_2 = get_info(p2)
                
                name1 = student_info_1["student_name"] if student_info_1 else "Unknown"
                name2 = student_info_2["student_name"] if student_info_2 else "Unknown"
                
                alerts.append({
                    "type": "students_too_close",
                    "severity": "high",
                    "details": f"Proximity alert: {name1} and {name2} are too close.",
                    "student_info": student_info_1, # Associate with first student
                    "bbox": p1.bbox
                })

    return alerts

def _iou(box1, box2) -> float:
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    if inter == 0:
        return 0.0
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    return inter / (area1 + area2 - inter + 1e-6)
