import datetime
from typing import List, Dict, Any

def check_conflicts(service, calendar_id, start_time, end_time, exclude_event_id=None):
    """
    Check for conflicts with existing events
    Returns list of conflicting events or empty list if none
    """
    # Get timeMin and timeMax from the event details
    try:
        # Extract datetime strings
        if isinstance(start_time, dict):
            start_str = start_time.get('dateTime')
            end_str = end_time.get('dateTime')
        else:
            start_str = start_time
            end_str = end_time
            
        # Ensure we have proper datetime strings
        if not start_str or not end_str:
            return []
            
        # Query events in this time range
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_str,
            timeMax=end_str,
            singleEvents=True
        ).execute()
        
        events = events_result.get('items', [])
        
        # Filter out the event being updated if provided
        if exclude_event_id:
            conflicts = [
                {
                    'id': event['id'],
                    'summary': event['summary'],
                    'start': event['start'],
                    'end': event['end']
                }
                for event in events if event.get('id') != exclude_event_id
            ]
        else:
            conflicts = [
                {
                    'id': event['id'],
                    'summary': event['summary'],
                    'start': event['start'],
                    'end': event['end']
                }
                for event in events
            ]
            
        return conflicts
        
    except Exception as e:
        print(f"Error checking conflicts: {e}")
        return []