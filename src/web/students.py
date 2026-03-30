import streamlit as st
import json
import os
import pandas as pd

def load_seat_config(config_path):
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading config: {e}")
            return None
    return None

def render():
    st.title("👥 Student Profiles")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    config_path = os.path.join(current_dir, "..", "config", "seats_config.json")
    
    seat_config = load_seat_config(config_path)
    
    if not seat_config:
        st.warning("No seat configuration found.")
        return

    # Convert to DataFrame for display
    students_data = []
    for info in seat_config.get('seats', []):
        seat_id = info.get('id')
        info['seat_id'] = seat_id
        students_data.append(info)
    
    df = pd.DataFrame(students_data)
    
    if df.empty:
        st.info("No students configured.")
        return

    # Student List
    st.subheader("Registered Students")
    st.dataframe(df[['seat_id', 'student_name', 'id', 'email']], use_container_width=True)

    # Student Detail View
    st.markdown("---")
    st.subheader("Student Details")
    
    selected_student = st.selectbox("Select Student", df['student_name'].unique())
    
    if selected_student:
        student_info = df[df['student_name'] == selected_student].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Name:** {student_info['student_name']}")
            st.markdown(f"**ID:** {student_info['id']}")
        with col2:
            st.markdown(f"**Email:** {student_info['email']}")
            st.markdown(f"**Seat ID:** {student_info['seat_id']}")

        # Placeholder for future stats (e.g., total alerts for this student)
        st.info("Alert history for this student will be implemented by correlating with logs.")
