import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime

def parse_logs(log_path):
    """Parses the email log file to extract stats."""
    if not os.path.exists(log_path):
        return pd.DataFrame()

    data = []
    current_entry = {}
    
    with open(log_path, 'r') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if line.startswith("To:"):
            current_entry['to'] = line.split(": ")[1]
        elif line.startswith("Subject:"):
            current_entry['subject'] = line.split(": ")[1]
        elif line.startswith("Time:"):
            try:
                ts = int(line.split(": ")[1])
                current_entry['timestamp'] = datetime.fromtimestamp(ts)
            except:
                current_entry['timestamp'] = datetime.now()
        elif line.startswith("Body:"):
            current_entry['body'] = line.split(": ", 1)[1]
        elif line.startswith("--- SIMULATED EMAIL ---"):
            current_entry = {}
        elif line.startswith("-----------------------"):
            if current_entry:
                data.append(current_entry)

    return pd.DataFrame(data)

def render():
    st.title("📊 Dashboard Overview")
    
    # Path to logs
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    log_path = os.path.join(project_root, "captures", "email_log.txt")

    df = parse_logs(log_path)

    # Metrics with Card Styling
    col1, col2, col3 = st.columns(3)
    
    total_alerts = len(df) if not df.empty else 0
    
    # Calculate recent alerts (last 24h)
    recent_alerts = 0
    if not df.empty and 'timestamp' in df.columns:
        last_24h = datetime.now().timestamp() - 86400
        recent_alerts = len(df[df['timestamp'] > datetime.fromtimestamp(last_24h)])

    with col1:
        st.markdown(f"""
        <div class="card">
            <h3 style="color: #60a5fa; margin: 0;">📊 Total Alerts</h3>
            <h1 style="margin: 0.5rem 0; color: #f1f5f9;">{total_alerts}</h1>
            <p style="color: #94a3b8; margin: 0;">All-time alerts generated</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="card">
            <h3 style="color: #fbbf24; margin: 0;">⚠️ Recent Alerts</h3>
            <h1 style="margin: 0.5rem 0; color: #f1f5f9;">{recent_alerts}</h1>
            <p style="color: #94a3b8; margin: 0;">Last 24 hours</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="card">
            <h3 style="color: #34d399; margin: 0;">📹 Active Cameras</h3>
            <h1 style="margin: 0.5rem 0; color: #f1f5f9;">1</h1>
            <p style="color: #94a3b8; margin: 0;">Currently monitoring</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Recent Activity Chart
    st.subheader("Alert Activity")
    if not df.empty and 'timestamp' in df.columns:
        # Group by hour
        df['hour'] = df['timestamp'].dt.floor('H')
        hourly_counts = df.groupby('hour').size()
        st.line_chart(hourly_counts)
    else:
        st.info("No activity data available yet.")

    # Recent Logs Preview
    st.subheader("Recent Alerts")
    if not df.empty:
        st.dataframe(
            df[['timestamp', 'subject', 'body']].sort_values('timestamp', ascending=False).head(5),
            use_container_width=True
        )
    else:
        st.info("No alerts recorded.")
