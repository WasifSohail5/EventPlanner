import pytz
from datetime import datetime
from tzlocal import get_localzone
import streamlit as st

def get_user_timezone():
    """Get the user's timezone"""
    try:
        local_tz = get_localzone()
        return str(local_tz)
    except:
        return "Asia/Karachi"  # Default to Pakistan time

def format_datetime(dt_string, timezone_str=None):
    """Format datetime with timezone conversion"""
    try:
        # Parse the datetime string
        if dt_string.endswith('Z'):
            # UTC time format
            dt = datetime.fromisoformat(dt_string[:-1])
            dt = dt.replace(tzinfo=pytz.UTC)
        else:
            # ISO format with potential timezone
            dt = datetime.fromisoformat(dt_string)
            
        # Get the target timezone
        if timezone_str is None:
            if 'timezone' in st.session_state:
                timezone_str = st.session_state.timezone
            else:
                timezone_str = get_user_timezone()
        
        # Convert to target timezone
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
            
        target_tz = pytz.timezone(timezone_str)
        dt = dt.astimezone(target_tz)
        
        # Format for display
        return dt.strftime("%Y-%m-%d %I:%M %p")
        
    except Exception as e:
        print(f"Error formatting datetime: {e}")
        return dt_string  # Return original if conversion fails

def get_iso_datetime(date, time, timezone_str=None):
    """Convert date and time to ISO format with timezone"""
    if timezone_str is None:
        timezone_str = get_user_timezone()
    
    try:
        tz = pytz.timezone(timezone_str)
        dt = datetime.combine(date, time)
        dt = tz.localize(dt)
        return dt.isoformat()
    except Exception as e:
        print(f"Error creating ISO datetime: {e}")
        # Return basic ISO format as fallback
        return datetime.combine(date, time).isoformat()

def get_all_timezones():
    """Get list of all available timezones"""
    return pytz.all_timezones