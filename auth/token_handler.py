import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import streamlit as st

# If modifying these SCOPES, delete the file token.pkl.
SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'auth', 'token.pkl')
CREDS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'auth', 'credentials.json')

@st.cache_resource
def get_calendar_service():
    """
    Authenticate and create Google Calendar service.
    Uses token caching for persistent authentication.
    """
    creds = None
    
    # Check if token file exists and load it
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            try:
                creds = pickle.load(token)
            except Exception as e:
                st.error(f"Error loading credentials: {e}")
                creds = None
    
    # If no valid credentials, do the authorization flow
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDS_PATH):
                    st.error("Missing credentials.json file. Please place it in the auth folder.")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
        except Exception as e:
            st.error(f"Authentication error: {e}")
            return None
    
    # Build and return the service
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        st.error(f"Error building service: {e}")
        return None