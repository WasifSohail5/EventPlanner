import streamlit as st
import datetime
import pandas as pd
from backend import calendar_utils, timezone

def show(service):
    """Event viewer and search page"""
    st.title("📋 Calendar Events")
    
    # Top filters
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        calendars = calendar_utils.get_calendars(service)
        calendar_options = {cal["name"]: cal["id"] for cal in calendars}
        calendar_name = st.selectbox(
            "Calendar", 
            options=list(calendar_options.keys()),
            index=0
        )
        calendar_id = calendar_options.get(calendar_name, 'primary')
        
    with col2:
        date_range = st.selectbox(
            "Date Range",
            ["Next 7 days", "Next 30 days", "Next 90 days", "Custom Range"]
        )
        
    with col3:
        search_button = st.button("🔄 Refresh")
    
    # Search box
    search_query = st.text_input("🔍 Search Events", placeholder="Search by title, description...")
    
    # Handle custom date range
    if date_range == "Custom Range":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.date.today())
        with col2:
            end_date = st.date_input("End Date", datetime.date.today() + datetime.timedelta(days=30))
            
        time_min = datetime.datetime.combine(start_date, datetime.time.min).isoformat() + 'Z'
        time_max = datetime.datetime.combine(end_date, datetime.time.max).isoformat() + 'Z'
    else:
        # Calculate time range based on selection
        today = datetime.date.today()
        if date_range == "Next 7 days":
            days = 7
        elif date_range == "Next 30 days":
            days = 30
        elif date_range == "Next 90 days":
            days = 90
        else:
            days = 30  # Default
            
        time_min = datetime.datetime.combine(today, datetime.time.min).isoformat() + 'Z'
        time_max = datetime.datetime.combine(today + datetime.timedelta(days=days), 
                                           datetime.time.max).isoformat() + 'Z'
    
    # Get events (either from cache or API)
    st.session_state.setdefault('force_refresh', False)
    if search_button:
        st.session_state.force_refresh = True
        
    use_cache = not st.session_state.force_refresh
    events = calendar_utils.get_events(
        service, 
        calendar_id=calendar_id, 
        time_min=time_min, 
        time_max=time_max, 
        use_cache=use_cache,
        search_query=search_query
    )
    st.session_state.force_refresh = False
    
    if not events:
        st.info("No events found in the selected time range")
    else:
        # Tab navigation
        list_tab, calendar_tab, export_tab = st.tabs(["List View", "Calendar View", "Export"])
        
        with list_tab:
            for event in events:
                with st.expander(event.get('summary', 'Untitled Event'), expanded=False):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    # Format dates for display
                    if 'dateTime' in event.get('start', {}):
                        start_str = timezone.format_datetime(
                            event['start']['dateTime'],
                            event['start'].get('timeZone')
                        )
                    else:
                        start_str = event.get('start', {}).get('date', 'N/A')
                        
                    if 'dateTime' in event.get('end', {}):
                        end_str = timezone.format_datetime(
                            event['end']['dateTime'],
                            event['end'].get('timeZone')
                        )
                    else:
                        end_str = event.get('end', {}).get('date', 'N/A')
                    
                    with col1:
                        st.markdown(f"**Time:** {start_str} to {end_str}")
                        
                        if event.get('location'):
                            st.markdown(f"**Location:** {event['location']}")
                            
                        if event.get('description'):
                            st.markdown(f"**Description:**\n{event['description']}")
                    
                    with col2:
                        # Recurrence info
                        if event.get('recurrence'):
                            st.info("⟳ Recurring event")
                            
                        # Attendees
                        attendees = event.get('attendees', [])
                        if attendees:
                            st.markdown("**Attendees:**")
                            for attendee in attendees[:5]:  # Show first 5
                                status = attendee.get('responseStatus', 'needsAction')
                                icon = "❓"
                                if status == 'accepted':
                                    icon = "✅"
                                elif status == 'declined':
                                    icon = "❌"
                                elif status == 'tentative':
                                    icon = "⚠️"
                                    
                                st.markdown(f"{icon} {attendee.get('email')}")
                                
                            if len(attendees) > 5:
                                st.markdown(f"...and {len(attendees) - 5} more")
                    
                    with col3:
                        # Actions
                        if st.button("Delete", key=f"del_{event.get('id')}", type="primary"):
                            # Confirm deletion
                            if st.session_state.get(f"confirm_{event.get('id')}", False):
                                # Delete the event
                                result = calendar_utils.delete_event(
                                    service,
                                    calendar_id,
                                    event.get('id')
                                )
                                
                                if result['success']:
                                    st.success(result['message'])
                                    st.rerun()
                                else:
                                    st.error(result['message'])
                            else:
                                # Set confirmation state and show prompt
                                st.session_state[f"confirm_{event.get('id')}"] = True
                                st.warning("Click 'Delete' again to confirm")

        with calendar_tab:
            # Group events by date
            date_events = {}
            for event in events:
                if 'dateTime' in event.get('start', {}):
                    date_str = event['start']['dateTime'][:10]  # YYYY-MM-DD
                else:
                    date_str = event.get('start', {}).get('date', '')
                    
                if date_str:
                    if date_str not in date_events:
                        date_events[date_str] = []
                    date_events[date_str].append(event)
            
            # Sort dates
            sorted_dates = sorted(date_events.keys())
            
            # Show events by date
            for date_str in sorted_dates:
                # Format date header
                try:
                    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%A, %B %d, %Y')
                    
                    # Check if this is today
                    today = datetime.date.today().strftime('%Y-%m-%d')
                    if date_str == today:
                        st.subheader(f"📌 TODAY - {formatted_date}")
                    else:
                        st.subheader(f"📆 {formatted_date}")
                except:
                    st.subheader(f"📆 {date_str}")
                
                # Display events for this date
                for event in date_events[date_str]:
                    # Extract time for display
                    if 'dateTime' in event.get('start', {}):
                        time_str = timezone.format_datetime(
                            event['start']['dateTime'],
                            event['start'].get('timeZone')
                        ).split()[1]  # Just time portion
                    else:
                        time_str = "All day"
                        
                    # Card styling
                    card_style = """
                        padding: 10px;
                        border-radius: 5px;
                        margin-bottom: 10px;
                        background-color: #f0f8ff;
                        border-left: 4px solid #4285F4;
                    """
                    
                    # Check for keywords to color code
                    summary = event.get('summary', '').lower()
                    if 'meeting' in summary:
                        card_style = card_style.replace("#4285F4", "#0F9D58")  # Green
                        card_style = card_style.replace("#f0f8ff", "#e6f4ea")
                    elif 'deadline' in summary:
                        card_style = card_style.replace("#4285F4", "#DB4437")  # Red
                        card_style = card_style.replace("#f0f8ff", "#fce8e6")
                    elif 'birthday' in summary or 'celebration' in summary:
                        card_style = card_style.replace("#4285F4", "#F4B400")  # Yellow
                        card_style = card_style.replace("#f0f8ff", "#fef7e0")
                    
                    st.markdown(
                        f"""
                        <div style="{card_style}">
                            <strong>{time_str}</strong> - {event.get('summary', 'Untitled Event')}
                            <div><small>{event.get('location', '')}</small></div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
        with export_tab:
            st.subheader("📤 Export Events")
            
            export_format = st.selectbox("Format", ["JSON", "CSV"])
            
            if st.button("Generate Export"):
                format_type = export_format.lower()
                export_data = calendar_utils.export_events(events, format_type)
                
                # Create download button
                st.download_button(
                    label=f"Download as {export_format}",
                    data=export_data,
                    file_name=f"calendar_events.{format_type}",
                    mime=f"application/{format_type}"
                )