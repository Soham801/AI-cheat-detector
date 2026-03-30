import streamlit as st
import pandas as pd
import os
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
        elif line.startswith("Attachment:"):
            current_entry['attachment'] = line.split(": ", 1)[1]
        elif line.startswith("--- SIMULATED EMAIL ---"):
            current_entry = {}
        elif line.startswith("-----------------------"):
            if current_entry:
                data.append(current_entry)

    return pd.DataFrame(data)

def render():
    st.title("📧 Email Logs & Alerts")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    log_path = os.path.join(project_root, "captures", "email_log.txt")
    
    if st.button("🔄 Refresh Logs", use_container_width=False):
        st.rerun()

    df = parse_logs(log_path)
    
    if df.empty:
        st.info("No logs found.")
        return

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("Search Subject/Body")
    with col2:
        if 'timestamp' in df.columns:
            # Date filter could go here
            pass

    # Apply filters
    if search_term:
        df = df[df['subject'].str.contains(search_term, case=False) | 
                df['body'].str.contains(search_term, case=False)]

    # Display logs
    st.dataframe(
        df[['timestamp', 'to', 'subject', 'body']],
        use_container_width=True,
        height=400
    )

    # Detail View
    st.subheader("Log Details")
    selected_index = st.number_input("Enter Row Index to View Details", min_value=0, max_value=len(df)-1, value=0, step=1)
    
    if not df.empty and 0 <= selected_index < len(df):
        row = df.iloc[selected_index]
        st.markdown(f"**Time:** {row['timestamp']}")
        st.markdown(f"**To:** {row['to']}")
        st.markdown(f"**Subject:** {row['subject']}")
        st.info(row['body'])
        
        if 'attachment' in row and row['attachment']:
            if os.path.exists(row['attachment']):
                st.image(row['attachment'], caption="Evidence Snapshot")
            else:
                st.warning(f"Attachment not found: {row['attachment']}")
