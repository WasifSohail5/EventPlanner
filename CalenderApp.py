import streamlit as st
from datetime import datetime, timedelta
import pytz
import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# --------- Setup ---------
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None

# --------- Load Credentials ---------
if os.path.exists('token.pkl'):
    with open('token.pkl', 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(r'E:\BSAI-5th\DataMining\MedNexusAI\credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

    with open(r'E:\BSAI-5th\DataMining\MedNexusAI\token.pkl', 'wb') as token:
        pickle.dump(creds, token)

# --------- Google Calendar API Service ---------
service = build('calendar', 'v3', credentials=creds)

# --------- Streamlit UI ---------
st.set_page_config(page_title="Google Calendar App", page_icon="📅", layout="centered")

st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📅 Google Calendar Manager</h1>", unsafe_allow_html=True)

menu = st.sidebar.selectbox("Choose Action", ["📆 View Events", "➕ Create Event"])

if menu == "📆 View Events":
    st.subheader("📋 Upcoming Events (Next 7 Days)")
    now = datetime.utcnow().isoformat() + 'Z'
    end_time = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary', timeMin=now, timeMax=end_time,
        maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        st.info("No upcoming events found.")
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            st.success(f"🕒 {start} - {event['summary']}")

elif menu == "➕ Create Event":
    st.subheader("📌 Create New Event")

    title = st.text_input("Event Title")
    description = st.text_area("Event Description")
    location = st.text_input("Location")
    date = st.date_input("Date", datetime.now())
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    timezone = "Asia/Karachi"

    if st.button("Create Event"):
        try:
            start_dt = datetime.combine(date, start_time).astimezone(pytz.timezone(timezone)).isoformat()
            end_dt = datetime.combine(date, end_time).astimezone(pytz.timezone(timezone)).isoformat()

            event = {
                'summary': title,
                'location': location,
                'description': description,
                'start': {'dateTime': start_dt, 'timeZone': timezone},
                'end': {'dateTime': end_dt, 'timeZone': timezone},
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }

            created_event = service.events().insert(calendarId='primary', body=event).execute()
            st.success(f"✅ Event Created: [Open in Google Calendar]({created_event.get('htmlLink')})")
        except Exception as e:
            st.error(f"❌ Failed to create event: {e}")
