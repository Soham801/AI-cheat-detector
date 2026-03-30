import streamlit as st
import os
from datetime import datetime
import base64

def render():
    st.title("📸 Screenshot Gallery")
    
    # Get captures directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    captures_dir = os.path.join(project_root, "captures")
    
    if not os.path.exists(captures_dir):
        st.warning("No captures directory found.")
        return
    
    # Get all screenshot files
    screenshots = []
    for file in os.listdir(captures_dir):
        if file.endswith('.jpg') and file.startswith('cheat_alert_'):
            filepath = os.path.join(captures_dir, file)
            # Parse filename: cheat_alert_{student_id}_{timestamp}.jpg
            parts = file.replace('.jpg', '').split('_')
            if len(parts) >= 3:
                student_id = parts[2]
                timestamp = int(parts[3]) if len(parts) > 3 else 0
                screenshots.append({
                    'path': filepath,
                    'filename': file,
                    'student_id': student_id,
                    'timestamp': timestamp,
                    'datetime': datetime.fromtimestamp(timestamp) if timestamp > 0 else datetime.now()
                })
    
    # Sort by timestamp (newest first)
    screenshots.sort(key=lambda x: x['timestamp'], reverse=True)
    
    if not screenshots:
        st.info("📷 No screenshots captured yet. Screenshots will appear here when cheating is detected.")
        return
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="card">
            <h3 style="color: #60a5fa; margin: 0;">📊 Total Captures</h3>
            <h1 style="margin: 0.5rem 0; color: #f1f5f9;">{len(screenshots)}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        today_count = sum(1 for s in screenshots if s['datetime'].date() == datetime.now().date())
        st.markdown(f"""
        <div class="card">
            <h3 style="color: #fbbf24; margin: 0;">📅 Today</h3>
            <h1 style="margin: 0.5rem 0; color: #f1f5f9;">{today_count}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        unique_students = len(set(s['student_id'] for s in screenshots))
        st.markdown(f"""
        <div class="card">
            <h3 style="color: #34d399; margin: 0;">👥 Students</h3>
            <h1 style="margin: 0.5rem 0; color: #f1f5f9;">{unique_students}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filter options
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        filter_student = st.selectbox(
            "🔍 Filter by Student",
            ["All Students"] + sorted(list(set(s['student_id'] for s in screenshots)))
        )
    
    with col_filter2:
        filter_date = st.selectbox(
            "📅 Filter by Date",
            ["All Dates", "Today", "Last 7 Days", "Last 30 Days"]
        )
    
    # Apply filters
    filtered_screenshots = screenshots.copy()
    
    if filter_student != "All Students":
        filtered_screenshots = [s for s in filtered_screenshots if s['student_id'] == filter_student]
    
    if filter_date == "Today":
        filtered_screenshots = [s for s in filtered_screenshots if s['datetime'].date() == datetime.now().date()]
    elif filter_date == "Last 7 Days":
        from datetime import timedelta
        week_ago = datetime.now() - timedelta(days=7)
        filtered_screenshots = [s for s in filtered_screenshots if s['datetime'] >= week_ago]
    elif filter_date == "Last 30 Days":
        from datetime import timedelta
        month_ago = datetime.now() - timedelta(days=30)
        filtered_screenshots = [s for s in filtered_screenshots if s['datetime'] >= month_ago]
    
    st.markdown(f"**Showing {len(filtered_screenshots)} of {len(screenshots)} screenshots**")
    
    st.markdown("---")
    
    # Display screenshots in grid
    cols_per_row = 3
    for i in range(0, len(filtered_screenshots), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(filtered_screenshots):
                shot = filtered_screenshots[idx]
                with col:
                    st.image(shot['path'], use_container_width=True)
                    st.markdown(f"""
                    <div style="background-color: #1e293b; padding: 0.75rem; border-radius: 8px; margin-top: -10px;">
                        <p style="margin: 0; color: #60a5fa; font-weight: 600;">🚨 {shot['student_id']}</p>
                        <p style="margin: 0; color: #94a3b8; font-size: 0.85rem;">
                            📅 {shot['datetime'].strftime('%Y-%m-%d')}<br>
                            ⏰ {shot['datetime'].strftime('%H:%M:%S')}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Download button
                    with open(shot['path'], "rb") as file:
                        btn = st.download_button(
                            label="⬇️ Download",
                            data=file,
                            file_name=shot['filename'],
                            mime="image/jpeg",
                            key=f"download_{idx}",
                            use_container_width=True
                        )
                    
                    st.markdown("---")
