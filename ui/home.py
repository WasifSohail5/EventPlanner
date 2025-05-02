import streamlit as st
import datetime
import pandas as pd
import plotly.graph_objects as go
from backend import calendar_utils, timezone

def show(service):
    """Home dashboard with calendar overview"""
    
    st.title("🏠 Calendar Dashboard")
    
    # Get today's date
    today = datetime.datetime.now().date()
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("📅 Quick Stats")
        
        # Fetch data for next 7 days
        time_min = datetime.datetime.combine(today, datetime.time.min).isoformat() + 'Z'
        time_max = datetime.datetime.combine(today + datetime.timedelta(days=7), 
                                           datetime.time.max).isoformat() + 'Z'
        
        events = calendar_utils.get_events(service, time_min=time_min, time_max=time_max)
        
        # Stats
        st.metric(label="Today's Events", 
                 value=len([e for e in events if e['start'].get('dateTime', '')[:10] == today.isoformat()]))
        st.metric(label="Week's Events", value=len(events))
        
        # Calendar selection
        st.subheader("📁 Your Calendars")
        calendars = calendar_utils.get_calendars(service)
        
        for cal in calendars:
            st.checkbox(cal['name'], key=f"cal_{cal['id']}", value=(cal['id'] == 'primary'))
    
    with col1:
        st.subheader("📑 Today's Schedule")
        
        # Today's events
        today_events = [e for e in events if e['start'].get('dateTime', '')[:10] == today.isoformat()]
        
        if not today_events:
            st.info("No events scheduled for today")
        else:
            # Sort by start time
            today_events.sort(key=lambda x: x['start'].get('dateTime', ''))
            
            for event in today_events:
                with st.container():
                    col1, col2 = st.columns([1, 4])
                    
                    # Start time
                    start_time = timezone.format_datetime(
                        event['start'].get('dateTime', event['start'].get('date')),
                        event['start'].get('timeZone')
                    )
                    
                    # Display time and event
                    with col1:
                        st.write(start_time.split(' ')[1])  # Just time portion
                    
                    with col2:
                        # Card style based on event type
                        color = "#4285F4"  # Default Google blue
                        # Check for keywords to color code
                        summary = event.get('summary', '').lower()
                        if 'meeting' in summary:
                            color = "#0F9D58"  # Green for meetings
                        elif 'deadline' in summary:
                            color = "#DB4437"  # Red for deadlines
                        
                        st.markdown(
                            f"""
                            <div style="background-color: {color}22; border-left: 4px solid {color}; 
                                       padding: 10px; border-radius: 4px;">
                                <strong>{event.get('summary', 'Untitled Event')}</strong><br>
                                <small>{event.get('location', 'No location')} • 
                                      {start_time} to {timezone.format_datetime(
                                          event['end'].get('dateTime', event['end'].get('date')),
                                          event['end'].get('timeZone')
                                      ).split(' ')[1]}</small>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                    
                    st.write("")  # Spacing
        
        # Week visualization
        st.subheader("📊 Week at a Glance")
        
        # Create data for calendar heatmap
        date_counts = {}
        for i in range(7):
            date = today + datetime.timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            count = len([e for e in events if e['start'].get('dateTime', '')[:10] == date_str])
            date_counts[date_str] = count
            
        # Create DataFrame for visualization
        df = pd.DataFrame([
            {'date': date, 'count': count, 'day': datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%a')} 
            for date, count in date_counts.items()
        ])
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=df['day'], 
                y=df['count'],
                text=df['count'],
                textposition='auto',
                marker_color=['#4285F4' if d != today.strftime('%a') else '#DB4437' for d in df['day']]
            )
        ])
        
        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis_title='',
            yaxis_title='Events',
        )
        
        st.plotly_chart(fig, use_container_width=True)