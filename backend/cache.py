import os
import json
import time
from typing import List, Dict, Any, Optional

# Cache directory
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(CACHE_DIR, exist_ok=True)

# Cache expiration in seconds (4 hours)
CACHE_EXPIRATION = 4 * 60 * 60

def get_cache_path(calendar_id: str) -> str:
    """Get path to cache file for calendar"""
    safe_id = calendar_id.replace('@', '_').replace('.', '_')
    return os.path.join(CACHE_DIR, f"events_{safe_id}.json")

def cache_events(calendar_id: str, events: List[Dict[str, Any]]) -> None:
    """Save events to cache file"""
    try:
        cache_data = {
            'timestamp': time.time(),
            'events': events
        }
        
        with open(get_cache_path(calendar_id), 'w') as f:
            json.dump(cache_data, f)
    except Exception as e:
        print(f"Cache write error: {e}")

def get_cached_events(calendar_id: str) -> Optional[List[Dict[str, Any]]]:
    """Get events from cache if not expired"""
    cache_path = get_cache_path(calendar_id)
    
    if not os.path.exists(cache_path):
        return None
        
    try:
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
            
        # Check if cache is expired
        if time.time() - cache_data['timestamp'] > CACHE_EXPIRATION:
            return None
            
        return cache_data['events']
    except Exception as e:
        print(f"Cache read error: {e}")
        return None

def add_event_to_cache(calendar_id: str, event: Dict[str, Any]) -> None:
    """Add new event to cache"""
    events = get_cached_events(calendar_id) or []
    events.append(event)
    cache_events(calendar_id, events)

def remove_event_from_cache(calendar_id: str, event_id: str) -> None:
    """Remove event from cache"""
    events = get_cached_events(calendar_id)
    if events:
        events = [evt for evt in events if evt.get('id') != event_id]
        cache_events(calendar_id, events)

def update_cached_event(calendar_id: str, updated_event: Dict[str, Any]) -> None:
    """Update existing event in cache"""
    events = get_cached_events(calendar_id)
    if events:
        event_id = updated_event.get('id')
        events = [evt if evt.get('id') != event_id else updated_event for evt in events]
        cache_events(calendar_id, events)

def clear_cache(calendar_id: str = None) -> None:
    """Clear cache for specific calendar or all calendars"""
    if calendar_id:
        cache_path = get_cache_path(calendar_id)
        if os.path.exists(cache_path):
            os.remove(cache_path)
    else:
        for file in os.listdir(CACHE_DIR):
            if file.startswith('events_'):
                os.remove(os.path.join(CACHE_DIR, file))