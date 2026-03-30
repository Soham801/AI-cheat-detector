# AI Cheat Detector 🎓

AI Cheat Detector is an advanced, real-time computer vision system designed to monitor students during examinations and automatically detect suspicious or cheating behaviors. It leverages the power of YOLO object and pose detection models combined with a modern, dark-themed admin dashboard built on Streamlit.

---

## 🚀 Features

The system actively monitors a live camera feed and applies a robust rules engine to detect various cheating scenarios:

### 1. Advanced Cheating Rules
- **Head Pose Tracking:** Detects if a student is consistently looking left or right for an extended period (configurable time threshold). It achieves this by analyzing facial keypoints (eyes and nose) to calculate head direction with temporal smoothing.
- **Prohibited Item Detection:** Automatically identifies unauthorized objects such as mobile phones or suspicious materials (books/chits) within a student's proximity.
- **Seat Occupancy Monitoring:** Triggers high-severity alerts if multiple individuals are detected sharing a single seat or desk.
- **Proximity Alerts:** Measures physical distances between students and alerts administrators if students are sitting too close to each other.

### 2. Automated Action & Evidence Collection
- **Evidence Snapshots:** Automatically saves a high-resolution screenshot containing bounding boxes to the `captures/` directory whenever a cheating rule is violated.
- **Email Notifications:** Triggers automatic email alerts to administrators or invigilators attached with the captured screenshot of the violation. A built-in cooldown mechanism prevents email spamming for continuous violations.

### 3. Professional Admin Dashboard
Built using **Streamlit**, the web UI features a sleek, dark-themed professional design with the following navigation tabs:
- **📊 Dashboard:** High-level analytics and metrics of examination sessions.
- **📹 Live Monitoring:** Streams the real-time camera feed overlaid with detection boxes and live alert popups.
- **📧 Email Logs:** A log history of all automated email alerts sent out by the system.
- **👥 Student Profiles:** Management interface for student records and seating configurations.
- **📸 Screenshots:** Gallery view to review captured evidence of anomalous actions.
- **⚙️ Settings:** Configuration controls to adjust detection sensitivities and thresholds.

---

## 🛠️ Technology Stack

**Language:**
- **Python 3.x**

**Frameworks & Libraries:**
- **Ultralytics (YOLOv8):** Used as the core AI inference engine. The project utilizes `yolov8n-pose.pt`, `yolov8m-pose.pt` for pose estimation, and `yolov8s.pt` for object detection.
- **OpenCV (`opencv-contrib-python`):** Handles camera streaming, frame manipulation, and drawing bounding boxes/overlays.
- **Streamlit:** Powers the responsive, responsive frontend web application.
- **NumPy:** Used heavily in the rules engine for geometric calculations, vector math, and calculating Intersection over Union (IoU).
- **Pandas & Plotly:** Used within the Streamlit interface for data manipulation and rendering interactive charts/analytics.

---

## ⚙️ How It Works

1. **Video Ingestion:** The system captures video frames from a connected webcam via OpenCV (running at 720p resolution for high accuracy).
2. **AI Inference:** Each frame is passed into the YOLO detector (`yolo_detector.py`), which simultaneously identifies:
   - Persons and their corresponding 17 body keypoints (pose estimation).
   - Objects like cell phones and books.
3. **Rules Evaluation:** The extracted bounding boxes and keypoints are sent to the `rules_engine.py`. 
   - It cross-references detections against a predefined JSON seating configuration.
   - It performs mathematical verifications (e.g., analyzing the distance between eyes relative to the nose to determine head gaze angle).
   - It checks the Intersection over Union (IoU) of "person" boxes against "prohibited object" boxes.
4. **Alerts & Logging:** If an anomaly is registered, the violation is logged, bounding boxes turn red, an evidence image is saved, and an email dispatch is initiated via `email_service.py`.

---

## 📁 Project Structure

```text
AICheatDetector/
├── captures/               # Directory where evidence screenshots are saved
├── data/                   # Temporary data storage or database files
├── models/                 # Cached YOLOv8 model weights (.pt files)
├── src/                    # Main source code directory
│   ├── config/             # Configuration files (e.g., seating configurations JSON)
│   ├── detection/          # AI logic (rules_engine.py, yolo_detector.py, head_pose.py)
│   ├── utils/              # Helper scripts (drawing tools, email sending services)
│   ├── web/                # Streamlit UI frontend modules (app.py, dashboard.py, etc.)
│   └── main.py             # Alternative local entry point for testing the detector without Web UI
├── requirements.txt        # Python dependencies
└── README.md               # Project Documentation
```

---

## 💻 Installation & Setup

1. **Clone the repository and change directory:**
   ```bash
   git clone <repository-url>
   cd AICheatDetector
   ```

2. **Create and activate a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Web Application (Streamlit Admin Portal):**
   ```bash
   streamlit run src/web/app.py
   ```

5. **Run the Local Headless Detector (Terminal Output):**
   ```bash
   python src/main.py
   ```
