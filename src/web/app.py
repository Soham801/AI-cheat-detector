import streamlit as st
import os
import sys

# Add project root to sys.path to allow imports from src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_path = os.path.join(project_root, 'src')

# Add src to sys.path for detection/utils imports
if src_path not in sys.path:
    sys.path.append(src_path)

# Add current dir (src/web) to sys.path for sibling imports
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import pages directly
import dashboard
import live_feed
import logs
import students
import screenshots

st.set_page_config(
    page_title="AI Cheat Detector Admin",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Theme Professional Design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Dark Theme */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }
    
    /* Main content area */
    .main {
        background-color: transparent;
    }
    
    /* Sidebar Dark Theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] .stRadio > label {
        background-color: transparent !important;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    [data-testid="stSidebar"] .stRadio > label:hover {
        background-color: rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #f1f5f9 !important;
        font-weight: 600;
    }
    
    h1 {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Dark Cards */
    .card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.5rem;
        border: 1px solid #475569;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(59, 130, 246, 0.2);
    }
    
    /* Modern Buttons with Icons */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        letter-spacing: 0.5px;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Download Buttons */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
        transform: translateY(-2px);
    }
    
    /* Toggle/Checkbox Styling */
    .stCheckbox {
        background-color: #1e293b;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #475569;
    }
    
    /* Input Fields */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Dataframes */
    [data-testid="stDataFrame"] {
        background-color: #1e293b;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        border: 1px solid #475569;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #475569;
    }
    
    [data-testid="stMetric"] label {
        color: #94a3b8 !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-size: 2rem !important;
    }
    
    /* Info/Warning/Error boxes */
    .stAlert {
        background-color: #1e293b !important;
        border: 1px solid #475569 !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
    }
    
    /* Slider */
    .stSlider>div>div>div {
        background-color: #475569;
    }
    
    .stSlider>div>div>div>div {
        background-color: #3b82f6;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1e293b;
        border-radius: 12px;
        border: 1px solid #475569;
        color: #e2e8f0;
    }
    
    /* Custom Alert Styling */
    .alert-high {
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #ef4444;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
    }
    
    .alert-medium {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #fbbf24;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    st.sidebar.title("🎓 Admin Portal")
    
    page = st.sidebar.radio(
        "Navigation",
        ["📊 Dashboard", "📹 Live Monitoring", "📧 Email Logs", "👥 Student Profiles", "📸 Screenshots", "⚙️ Settings"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "**AI Cheat Detector**\n\n"
        "System Status: 🟢 Online\n"
        "Version: 2.0.0"
    )

    if page == "📊 Dashboard":
        dashboard.render()
    elif page == "📹 Live Monitoring":
        live_feed.render()
    elif page == "📧 Email Logs":
        logs.render()
    elif page == "👥 Student Profiles":
        students.render()
    elif page == "📸 Screenshots":
        screenshots.render()
    elif page == "⚙️ Settings":
        import settings
        settings.render()

if __name__ == "__main__":
    main()
