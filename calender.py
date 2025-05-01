import tkinter as tk
from tkinter import messagebox
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def create_event():
    creds = authenticate_google()
    service = build('calendar', 'v3', credentials=creds)

    title = title_entry.get()
    description = desc_entry.get()
    start_time = start_entry.get()
    end_time = end_entry.get()

    try:
        event = {
            'summary': title,
            'location': 'Online',
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Karachi',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Karachi',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        messagebox.showinfo("Success", f"Event created: {event.get('htmlLink')}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create event: {str(e)}")

# GUI Setup
root = tk.Tk()
root.title("Google Calendar Event Creator")
root.geometry("400x300")

tk.Label(root, text="Title:").pack()
title_entry = tk.Entry(root, width=40)
title_entry.pack()

tk.Label(root, text="Description:").pack()
desc_entry = tk.Entry(root, width=40)
desc_entry.pack()

tk.Label(root, text="Start (YYYY-MM-DDTHH:MM:SS):").pack()
start_entry = tk.Entry(root, width=40)
start_entry.pack()

tk.Label(root, text="End (YYYY-MM-DDTHH:MM:SS):").pack()
end_entry = tk.Entry(root, width=40)
end_entry.pack()

tk.Button(root, text="Create Event", command=create_event).pack(pady=20)

root.mainloop()
