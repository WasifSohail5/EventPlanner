import datetime
from typing import Dict, List, Optional, Any
import streamlit as st
import json
import os
from googleapiclient.errors import HttpError
from backend import cache, timezone, conflict_checker

# Path for caching
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(CACHE_DIR, exist_ok=True)

def get_calendar_info(service) -> Dict[str, str]:
    """Get user calendar information"""
    try:
        profile = service.calendarList().get(calendarId='primary').execute()
        return {
            "name": profile.get("summary", "User"),
            "email": profile.get("id", ""),
        }
    except Exception:
        return {"name": "User", "email": ""}

def get_calendars(service) -> List[Dict[str, str]]:
    """Get list of user's calendars"""
    try:
        calendar_list = service.calendarList().list().execute()
        calendars = [
            {"id": cal["id"], "name": cal["summary"]} 
            for cal in calendar_list.get("items", [])
        ]
        return calendars
    except Exception as e:
        st.error(f"Error fetching calendars: {e}")
        return []

def get_events(service, calendar_id='primary', 
               time_min=None, time_max=None, max_results=50, 
               use_cache=True, search_query=None) -> List[Dict[str, Any]]:
    """
    Get events from Google Calendar with optional caching
    """
    if time_min is None:
        time_min = datetime.datetime.utcnow().isoformat() + 'Z'
    
    if time_max is None:
        time_max = (datetime.datetime.utcnow() + 
                   datetime.timedelta(days=30)).isoformat() + 'Z'
    
    # Check cache first if enabled
    if use_cache:
        cached_events = cache.get_cached_events(calendar_id)
        if cached_events:
            if search_query:
                return [evt for evt in cached_events 
                        if search_query.lower() in evt.get('summary', '').lower() or 
                           search_query.lower() in evt.get('description', '').lower()]
            return cached_events
    
    # Fetch from API if no cache or cache disabled
    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Format and clean events
        for event in events:
            # Convert start/end times to user's timezone
            if 'dateTime' in event.get('start', {}):
                event['start']['formatted'] = timezone.format_datetime(
                    event['start'].get('dateTime'), 
                    event['start'].get('timeZone')
                )
            if 'dateTime' in event.get('end', {}):
                event['end']['formatted'] = timezone.format_datetime(
                    event['end'].get('dateTime'), 
                    event['end'].get('timeZone')
                )
        
        # Cache results for future use
        cache.cache_events(calendar_id, events)
        
        # Filter by search query if provided
        if search_query:
            events = [evt for evt in events 
                      if search_query.lower() in evt.get('summary', '').lower() or 
                         search_query.lower() in evt.get('description', '').lower()]
                
        return events
    
    except HttpError as error:
        st.error(f"An error occurred: {error}")
        return []

def create_event(service, calendar_id, event_details):
    """Create a new calendar event"""
    try:
        # Check for conflicts
        conflicts = conflict_checker.check_conflicts(
            service, 
            calendar_id, 
            event_details['start'], 
            event_details['end']
        )
        
        if conflicts:
            return {
                'success': False,
                'conflicts': conflicts,
                'message': "Conflicting events found."
            }
            
        # Create the event
        event = service.events().insert(
            calendarId=calendar_id, 
            body=event_details
        ).execute()
        
        # Update cache
        cache.add_event_to_cache(calendar_id, event)
        
        return {
            'success': True,
            'event': event,
            'message': "Event created successfully!",
            'link': event.get('htmlLink')
        }
        
    except Exception as e:
        return {
            'success': False, 
            'message': f"Failed to create event: {str(e)}"
        }

def delete_event(service, calendar_id, event_id):
    """Delete a calendar event"""
    try:
        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        # Update cache
        cache.remove_event_from_cache(calendar_id, event_id)
        
        return {
            'success': True, 
            'message': "Event deleted successfully!"
        }
    except Exception as e:
        return {
            'success': False, 
            'message': f"Failed to delete event: {str(e)}"
        }

def update_event(service, calendar_id, event_id, event_details):
    """Update an existing event"""
    try:
        # First check conflicts excluding this event
        conflicts = conflict_checker.check_conflicts(
            service,
            calendar_id,
            event_details['start'],
            event_details['end'],
            exclude_event_id=event_id
        )
        
        if conflicts:
            return {
                'success': False,
                'conflicts': conflicts,
                'message': "Conflicting events found."
            }
            
        # Update the event
        event = service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event_details
        ).execute()
        
        # Update cache
        cache.update_cached_event(calendar_id, event)
        
        return {
            'success': True,
            'event': event,
            'message': "Event updated successfully!"
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Failed to update event: {str(e)}"
        }

def export_events(events, format_type='json'):
    """Export events to specified format"""
    if format_type == 'json':
        return json.dumps(events, indent=2)
    elif format_type == 'csv':
        # Simple CSV conversion
        csv_data = "Summary,Start,End,Location,Description\n"
        for event in events:
            summary = event.get('summary', '').replace(',', ' ')
            start = event.get('start', {}).get('formatted', '')
            end = event.get('end', {}).get('formatted', '')
            location = event.get('location', '').replace(',', ' ')
            description = event.get('description', '').replace(',', ' ').replace('\n', ' ')
            csv_data += f"{summary},{start},{end},{location},{description}\n"
        return csv_data
    else:
        return "Unsupported format"

def get_writable_calendars(service) -> List[Dict[str, str]]:
    """Get list of calendars where user has write access"""
    try:
        calendar_list = service.calendarList().list().execute()
        writable_calendars = [
            {"id": cal["id"], "name": cal["summary"]}
            for cal in calendar_list.get("items", [])
            if cal.get("accessRole") in ["owner", "writer"]
        ]
        return writable_calendars
    except Exception as e:
        st.error(f"Error fetching calendars: {e}")
        return []