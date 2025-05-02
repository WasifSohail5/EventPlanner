import streamlit as st
import datetime
from backend import calendar_utils, timezone


def show(service):
    """Event creation form"""
    st.title("➕ Create New Event")

    # Tabs for basic and advanced
    basic_tab, advanced_tab = st.tabs(["Basic Info", "Advanced Options"])

    with basic_tab:
        # Basic event information
        title = st.text_input("Event Title", placeholder="Meeting with Team")

        col1, col2 = st.columns(2)
        with col1:
            event_date = st.date_input("Date", datetime.date.today())

        with col2:
            event_type = st.selectbox(
                "Event Type",
                ["🏢 Meeting", "🎓 Training", "🎉 Social", "💼 Work", "🏥 Medical", "✨ Other"]
            )

        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("Start Time", datetime.time(9, 0))
        with col2:
            end_time = st.time_input("End Time", datetime.time(10, 0))

        description = st.text_area("Description", placeholder="Meeting agenda or notes...")
        location = st.text_input("Location", placeholder="Office Meeting Room / Google Meet")

    with advanced_tab:
        # Calendar selection - MODIFIED to only show writable calendars
        calendars = calendar_utils.get_writable_calendars(service)  # New method to get only writable calendars

        if not calendars:
            st.error("No writable calendars found. You need a calendar with write access to create events.")
            st.stop()

        calendar_options = {cal["name"]: cal["id"] for cal in calendars}
        calendar_id = st.selectbox(
            "Calendar",
            options=list(calendar_options.keys()),
            format_func=lambda x: x,
            index=0
        )

        # Timezone selection
        all_timezones = timezone.get_all_timezones()
        user_timezone = st.session_state.get('timezone', 'Asia/Karachi')
        selected_timezone = st.selectbox(
            "Timezone",
            options=all_timezones,
            index=all_timezones.index(user_timezone) if user_timezone in all_timezones else 0
        )

        # Rest of the function remains the same
        # Recurrence options
        recurrence_enabled = st.checkbox("Recurring Event")
        recurrence_rule = None

        if recurrence_enabled:
            recurrence_type = st.selectbox(
                "Recurrence Pattern",
                ["Daily", "Weekly", "Monthly", "Custom"]
            )

            col1, col2 = st.columns(2)
            with col1:
                recurrence_count = st.number_input("Number of occurrences", min_value=1, value=2)

            if recurrence_type == "Daily":
                recurrence_rule = f"RRULE:FREQ=DAILY;COUNT={recurrence_count}"
            elif recurrence_type == "Weekly":
                recurrence_rule = f"RRULE:FREQ=WEEKLY;COUNT={recurrence_count}"
            elif recurrence_type == "Monthly":
                recurrence_rule = f"RRULE:FREQ=MONTHLY;COUNT={recurrence_count}"
            else:
                recurrence_rule = st.text_input(
                    "Custom RRULE",
                    value=f"RRULE:FREQ=DAILY;COUNT={recurrence_count}",
                    help="Advanced: Use RRULE format (e.g., FREQ=WEEKLY;BYDAY=MO,WE,FR)"
                )

        # Reminders
        st.subheader("Reminders")
        use_default_reminders = st.checkbox("Use Default Reminders", value=True)

        reminders_config = {"useDefault": use_default_reminders}

        if not use_default_reminders:
            reminder_methods = []
            reminder_minutes = []

            # Email reminder
            email_reminder = st.checkbox("Email Reminder")
            if email_reminder:
                email_minutes = st.slider("Email minutes before", 5, 1440, 60)
                reminder_methods.append("email")
                reminder_minutes.append(email_minutes)

            # Popup reminder
            popup_reminder = st.checkbox("Popup Reminder")
            if popup_reminder:
                popup_minutes = st.slider("Popup minutes before", 0, 1440, 10)
                reminder_methods.append("popup")
                reminder_minutes.append(popup_minutes)

            # Create overrides
            if reminder_methods:
                reminders_config["overrides"] = [
                    {"method": method, "minutes": minutes}
                    for method, minutes in zip(reminder_methods, reminder_minutes)
                ]

        # Attendees
        st.subheader("Attendees")
        attendees_text = st.text_area(
            "Enter email addresses (one per line)",
            help="Add attendee emails, one per line"
        )

        attendees = []
        if attendees_text:
            for email in attendees_text.split('\n'):
                email = email.strip()
                if email and '@' in email:
                    attendees.append({"email": email})

    # Create event
    if st.button("📅 Create Event", type="primary"):
        if not title:
            st.error("Please enter an event title")
            return

        # Convert times to RFC3339 with timezone
        start_datetime = timezone.get_iso_datetime(event_date, start_time, selected_timezone)
        end_datetime = timezone.get_iso_datetime(event_date, end_time, selected_timezone)

        # Add emoji to title based on event type
        if event_type != "✨ Other":
            emoji = event_type.split()[0]
            if not title.startswith(emoji):
                title = f"{emoji} {title}"

        # Prepare event details
        event_details = {
            "summary": title,
            "location": location,
            "description": description,
            "start": {
                "dateTime": start_datetime,
                "timeZone": selected_timezone
            },
            "end": {
                "dateTime": end_datetime,
                "timeZone": selected_timezone
            },
            "reminders": reminders_config
        }

        # Add recurrence if enabled
        if recurrence_enabled and recurrence_rule:
            event_details["recurrence"] = [recurrence_rule]

        # Add attendees if provided
        if attendees:
            event_details["attendees"] = attendees

        # Use selected calendar
        selected_calendar_id = calendar_options.get(calendar_id, 'primary')

        # Create the event
        result = calendar_utils.create_event(service, selected_calendar_id, event_details)

        if result['success']:
            st.success(f"✅ {result['message']}")
            st.markdown(f"[View in Calendar]({result['link']})")
        else:
            st.error(f"❌ {result['message']}")

            # Show conflicts if any
            if 'conflicts' in result and result['conflicts']:
                st.warning("⚠️ Conflicting events:")
                for conflict in result['conflicts']:
                    start_time = timezone.format_datetime(
                        conflict['start'].get('dateTime', conflict['start'].get('date')),
                        conflict['start'].get('timeZone')
                    )
                    st.write(f"- {conflict['summary']} ({start_time})")