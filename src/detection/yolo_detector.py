# src/detection/yolo_detector.py

import os
from dataclasses import dataclass
from typing import List, Dict, Any

import cv2
import numpy as np
from ultralytics import YOLO


@dataclass
class PersonDetection:
    bbox: List[int]      # [x1, y1, x2, y2]
    conf: float
    keypoints: np.ndarray  # shape (17, 3) for YOLOv8 pose (x, y, conf)


@dataclass
class ObjectDetection:
    bbox: List[int]
    conf: float
    cls_name: str


class YOLODetector:
    def __init__(
        self,
        base_dir: str,
        obj_model_name: str = "yolov8n.pt", # Nano model - FASTEST
        pose_model_name: str = "yolov8n-pose.pt", # Nano pose - FASTEST
        device: str = "auto",  # Changed to auto-detect
    ):
        models_dir = os.path.join(base_dir, "models")
        obj_path = os.path.join(models_dir, obj_model_name)
        pose_path = os.path.join(models_dir, pose_model_name)

        # Auto-detect best device
        if device == "auto":
            import torch
            if torch.cuda.is_available():
                self.device = "cuda"
                print(f"🚀 GPU Detected! Using CUDA for acceleration")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device = "mps"
                print(f"🚀 Apple Silicon GPU Detected! Using MPS for acceleration")
            else:
                self.device = "cpu"
                print(f"⚠️ No GPU detected, using CPU (may be slower)")
        else:
            self.device = device

        # Load Object Detection Model
        if os.path.exists(obj_path):
            self.obj_model = YOLO(obj_path)
        else:
            print(f"Local model not found at {obj_path}, letting YOLO download {obj_model_name}...")
            self.obj_model = YOLO(obj_model_name)

        # Load Pose Estimation Model
        if os.path.exists(pose_path):
            self.pose_model = YOLO(pose_path)
        else:
            print(f"Local model not found at {pose_path}, letting YOLO download {pose_model_name}...")
            self.pose_model = YOLO(pose_model_name)

        # Enable half-precision for GPU (2x speedup)
        self.use_half = self.device in ["cuda", "mps"]
        if self.use_half:
            print(f"⚡ Enabling FP16 (half-precision) for faster inference")

        # Warmup models for optimal performance
        print(f"🔥 Warming up models...")
        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        self.obj_model.predict(dummy_frame, imgsz=640, device=self.device, verbose=False, half=self.use_half)
        self.pose_model.predict(dummy_frame, imgsz=640, device=self.device, verbose=False, half=self.use_half)
        print(f"✅ Models ready for high-performance detection!")

        # Map class IDs to human-readable names (adapt to your model)
        # For default COCO:
        self.id2name = {
            0: "person",
            67: "phone",
            63: "laptop",
            73: "book"      # Proxy for paper chit
        }

    def detect(self, frame) -> Dict[str, Any]:
        """
        Optimized detection with GPU acceleration and half-precision.
        Returns:
            {
              "persons": List[PersonDetection],
              "objects": List[ObjectDetection],
              "frame_size": (w, h)
            }
        """
        h, w = frame.shape[:2]

        # ---------- Object detection (phones, etc.) ----------
        # Optimized resolution for speed
        obj_results = self.obj_model.predict(
            frame, 
            imgsz=640,   # Optimized for speed
            conf=0.3,    # Standard threshold
            device=self.device, 
            verbose=False,
            half=self.use_half  # Use FP16 for speed
        )[0]

        objects: List[ObjectDetection] = []
        if obj_results.boxes is not None:
            for box in obj_results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = self.id2name.get(cls_id, str(cls_id))
                objects.append(ObjectDetection(bbox=[x1, y1, x2, y2],
                                               conf=conf,
                                               cls_name=cls_name))

        # ---------- Pose detection (head direction, posture) ----------
        # Optimized resolution for speed
        pose_results = self.pose_model.predict(
            frame, 
            imgsz=640,   # Optimized for speed
            device=self.device, 
            verbose=False,
            half=self.use_half  # Use FP16 for speed
        )[0]

        persons: List[PersonDetection] = []
        if pose_results.keypoints is not None:
            for kp, box, conf in zip(
                pose_results.keypoints.data,
                pose_results.boxes.xyxy,
                pose_results.boxes.conf
            ):
                x1, y1, x2, y2 = box.cpu().numpy().astype(int)
                kparr = kp.cpu().numpy()  # shape (17, 3)
                persons.append(
                    PersonDetection(
                        bbox=[x1, y1, x2, y2],
                        conf=float(conf.cpu().numpy()),
                        keypoints=kparr,
                    )
                )

        return {
            "persons": persons,
            "objects": objects,
            "frame_size": (w, h),
        }
