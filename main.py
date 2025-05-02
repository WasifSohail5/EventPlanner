import streamlit as st
import os
import sys
from datetime import datetime

# Add module paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
from auth import token_handler
from ui import home, event_creator, event_viewer, settings
from backend import calendar_utils, timezone

# Page configuration
st.set_page_config(
    page_title="Calendar Manager Pro",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom CSS
with open(os.path.join('assets', r'E:\BSAI-5th\DataMining\Event_Planner\assets\styles.css')) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'theme' not in st.session_state:
    st.session_state.theme = "light"
if 'primary_color' not in st.session_state:
    st.session_state.primary_color = "#4285F4"  # Google Blue

# Get Google Calendar service
service = token_handler.get_calendar_service()
if service:
    # Detect user timezone
    user_timezone = timezone.get_user_timezone()
    st.session_state.timezone = user_timezone
    
    # Sidebar navigation
    st.sidebar.title("📅 Calendar Manager Pro")
    
    # User info
    calendar_info = calendar_utils.get_calendar_info(service)
    st.sidebar.write(f"👤 Welcome, {calendar_info.get('name', 'User')}")
    st.sidebar.write(f"📧 {calendar_info.get('email', '')}")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "➕ Create Event", "📋 View Events", "⚙️ Settings"],
    )
    
    # Display selected page
    if page == "🏠 Home":
        home.show(service)
    elif page == "➕ Create Event":
        event_creator.show(service)
    elif page == "📋 View Events":
        event_viewer.show(service)
    elif page == "⚙️ Settings":
        settings.show()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info("Made with ❤️ by Wasif")
else:
    st.error("Authentication failed. Please check your credentials.")