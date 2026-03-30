import streamlit as st
import cv2
import numpy as np
import time
import os
import sys

# Import detection modules
# We assume sys.path is already set up in app.py
from detection.yolo_detector import YOLODetector
from detection.rules_engine import evaluate_cheating
from utils.drawing import draw_detections, draw_alerts
from utils.email_service import EmailService
import json

# Cache the detector to avoid reloading on every rerun
@st.cache_resource
def load_detector():
    # Find project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    return YOLODetector(base_dir=project_root, device="cpu")

@st.cache_resource
def load_email_service():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config", "email_config.json")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                if not config.get("simulation_mode", True):
                    return EmailService(
                        sender_email=config.get("sender_email", ""),
                        sender_password=config.get("sender_password", "")
                    )
        except Exception as e:
            st.warning(f"Could not load email config: {e}")
    
    return EmailService()  # Default to simulation mode

def load_seat_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config", "seats_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None

def render():
    st.title("📹 Live Monitoring")

    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3 style="color: #60a5fa; margin-top: 0;">🎛️ Controls</h3>
        </div>
        """, unsafe_allow_html=True)
        
        run_detection = st.toggle("🟢 Start Camera", value=False, help="Toggle to start/stop camera monitoring")
        
        st.markdown("---")
        
        confidence_threshold = st.slider(
            "🎯 Confidence Threshold",
            0.0, 1.0, 0.5, 0.05,
            help="Minimum confidence level for detections"
        )
        
        st.markdown("---")
        
        # Performance Settings
        frame_skip = st.slider(
            "⚡ Frame Skip (Performance)",
            1, 5, 3, 1,  # Changed default to 3 for better speed
            help="Process every Nth frame (higher = faster but less responsive)"
        )
        
        st.markdown("---")
        
        st.markdown("""
        <div class="card">
            <h4 style="color: #60a5fa; margin-top: 0;">📊 Performance</h4>
        </div>
        """, unsafe_allow_html=True)
        status_placeholder = st.empty()
        fps_placeholder = st.empty()
        
        st.markdown("---")
        
        # Screenshot Gallery
        st.markdown("""
        <div class="card">
            <h4 style="color: #60a5fa; margin-top: 0;">📸 Recent Captures</h4>
        </div>
        """, unsafe_allow_html=True)
        screenshot_gallery = st.empty()
        
    with col1:
        video_placeholder = st.empty()

    if run_detection:
        detector = load_detector()
        email_service = load_email_service()
        seat_config = load_seat_config()
        
        # Initialize camera with optimized settings
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)  # Set to 30 FPS
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer lag
        
        if not cap.isOpened():
            st.error("Could not open camera.")
            return

        status_placeholder.success("🟢 Monitoring Active")
        
        # Cooldown tracker
        if 'email_cooldowns' not in st.session_state:
            st.session_state.email_cooldowns = {}
        
        COOLDOWN_SECONDS = 10
        CAPTURES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "captures")
        os.makedirs(CAPTURES_DIR, exist_ok=True)

        stop_button = st.button("🛑 Stop", use_container_width=True)
        
        # Performance tracking
        import time
        frame_count = 0
        fps_start_time = time.time()
        last_detections = None
        last_alerts = None
        
        while run_detection and not stop_button:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to read frame.")
                break
            
            frame_count += 1
            
            # Frame skipping for performance
            if frame_count % frame_skip == 0:
                # Detection
                detections = detector.detect(frame)
                alerts = evaluate_cheating(detections, seat_config=seat_config)
                
                # Cache results
                last_detections = detections
                last_alerts = alerts
            else:
                # Use cached results for skipped frames
                detections = last_detections if last_detections else {"persons": [], "objects": [], "frame_size": (frame.shape[1], frame.shape[0])}
                alerts = last_alerts if last_alerts else []
            
            # Calculate FPS
            if frame_count % 30 == 0:
                fps_end_time = time.time()
                fps = 30 / (fps_end_time - fps_start_time)
                fps_placeholder.metric("⚡ FPS", f"{fps:.1f}")
                fps_start_time = time.time()
            
            # Handle Alerts
            for alert in alerts:
                if alert["severity"] == "high":
                    student_info = alert.get("student_info") or {"id": "unknown", "student_name": "Unknown", "email": None}
                    student_id = student_info["id"]
                    
                    last_time = st.session_state.email_cooldowns.get(student_id, 0)
                    if time.time() - last_time > COOLDOWN_SECONDS:
                        # Capture and Alert
                        timestamp = int(time.time())
                        filename = f"cheat_alert_{student_id}_{timestamp}.jpg"
                        filepath = os.path.join(CAPTURES_DIR, filename)
                        cv2.imwrite(filepath, frame)
                        
                        # Create organized alert details for email
                        from datetime import datetime
                        alert_details = {
                            'student_name': student_info.get('student_name', 'Unknown'),
                            'student_id': student_info.get('id', 'N/A'),
                            'violation_type': alert.get('details', 'Unknown Violation'),
                            'timestamp': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                            'severity': alert.get('severity', 'high')
                        }
                        
                        subject = f"🚨 Academic Integrity Alert: {student_info['student_name']}"
                        body = f"Cheating behavior detected: {alert['details']}\n\nSee attached evidence."
                        
                        # Send/Log with organized details
                        recipient = student_info.get("email")
                        if recipient:
                            email_service.send_alert(recipient, subject, body, filepath, alert_details)
                        else:
                            email_service.send_alert("LOG_ONLY", subject, body, filepath, alert_details)
                            
                        st.session_state.email_cooldowns[student_id] = time.time()
                        st.toast(f"📧 Alert sent for {student_info['student_name']}!", icon="⚠️")
                        
                        # Update screenshot gallery
                        if 'recent_screenshots' not in st.session_state:
                            st.session_state.recent_screenshots = []
                        
                        st.session_state.recent_screenshots.insert(0, {
                            'path': filepath,
                            'student': student_info['student_name'],
                            'time': datetime.fromtimestamp(timestamp).strftime('%H:%M:%S'),
                            'violation': alert.get('type', 'Unknown')
                        })
                        
                        # Keep only last 5 screenshots
                        st.session_state.recent_screenshots = st.session_state.recent_screenshots[:5]

            # Display screenshot gallery
            with screenshot_gallery:
                if 'recent_screenshots' in st.session_state and st.session_state.recent_screenshots:
                    for idx, shot in enumerate(st.session_state.recent_screenshots):
                        if os.path.exists(shot['path']):
                            st.image(shot['path'], caption=f"🚨 {shot['student']} - {shot['time']}", use_container_width=True)
                            if idx < len(st.session_state.recent_screenshots) - 1:
                                st.markdown("---")
                else:
                    st.info("📷 No captures yet. Screenshots will appear here when cheating is detected.")

            # Draw
            output = frame.copy()
            output = draw_detections(output, detections)
            output = draw_alerts(output, alerts)
            
            # Convert to RGB for Streamlit
            output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
            video_placeholder.image(output, channels="RGB", use_container_width=True)
            
        cap.release()
        status_placeholder.info("⚫ Monitoring Stopped")
    else:
        video_placeholder.info("Click '🟢 Start Camera' to begin monitoring.")


