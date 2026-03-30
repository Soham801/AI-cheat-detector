import streamlit as st
import json
import os

def load_email_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config", "email_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {"sender_email": "", "sender_password": "", "simulation_mode": True}

def save_email_config(config):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config", "email_config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

def render():
    st.title("⚙️ Settings")
    
    st.markdown("""
    <div class="card">
        <h2 style="margin-top: 0; color: #60a5fa;">📧 Email Configuration</h2>
        <p style="color: #94a3b8;">Configure the email account used to send cheating alerts to students.</p>
    </div>
    """, unsafe_allow_html=True)

    config = load_email_config()
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("email_settings_form"):
            st.subheader("Email Credentials")
            
            # Simulation Mode Toggle
            simulation_mode = st.toggle(
                "🔴 Simulation Mode (Log only, no real emails)",
                value=config.get("simulation_mode", True),
                help="When enabled, emails are logged to file instead of being sent"
            )
            
            if not simulation_mode:
                st.warning("⚠️ **Real Email Mode Active** - Use a Gmail App Password for security.")
            else:
                st.info("ℹ️ **Simulation Mode** - Alerts will be logged to `captures/email_log.txt`")
            
            st.markdown("---")
            
            sender_email = st.text_input(
                "📧 Sender Email (Gmail)",
                value=config.get("sender_email", ""),
                placeholder="your.email@gmail.com",
                disabled=simulation_mode
            )
            
            sender_password = st.text_input(
                "🔑 App Password",
                value=config.get("sender_password", ""),
                type="password",
                placeholder="Enter your Gmail App Password",
                disabled=simulation_mode,
                help="Generate an App Password: Google Account → Security → 2-Step Verification → App Passwords"
            )
            
            st.markdown("---")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submitted = st.form_submit_button("💾 Save Settings", use_container_width=True)
            with col_btn2:
                reset = st.form_submit_button("🔄 Reset to Default", use_container_width=True)
            
            if submitted:
                new_config = {
                    "sender_email": sender_email,
                    "sender_password": sender_password,
                    "simulation_mode": simulation_mode
                }
                save_email_config(new_config)
                st.success("✅ Settings saved successfully!")
                st.balloons()
                st.rerun()
            
            if reset:
                default_config = {
                    "sender_email": "",
                    "sender_password": "",
                    "simulation_mode": True
                }
                save_email_config(default_config)
                st.success("✅ Settings reset to default!")
                st.rerun()
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3 style="color: #60a5fa;">📖 Quick Guide</h3>
            <ol style="color: #94a3b8; font-size: 0.9rem;">
                <li>Enable/disable Simulation Mode</li>
                <li>Enter your Gmail credentials</li>
                <li>Click Save Settings</li>
                <li>Test in Live Monitoring</li>
            </ol>
            <hr style="border-color: #475569;">
            <p style="color: #94a3b8; font-size: 0.85rem;">
                <strong>Note:</strong> Never share your App Password. It provides full access to your Gmail account.
            </p>
        </div>
        """, unsafe_allow_html=True)

