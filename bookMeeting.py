import openai_secret_manager
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

# Set up the calendar service
secrets = openai_secret_manager.get_secrets("google")
creds = Credentials.from_authorized_user_info(info=secrets)
calendar_service = build('calendar', 'v3', credentials=creds)

# Ask the user to select a day
selected_day = input('Please select a day in the format YYYY-MM-DD: ')

# Get the calendar events for the selected day
events_result = calendar_service.events().list(calendarId='primary', timeMin=selected_day+'T00:00:00Z',
                                              timeMax=selected_day+'T23:59:59Z', singleEvents=True,
                                              orderBy='startTime').execute()
events = events_result.get('items', [])

# Get the available times for the selected day
available_times = []
for event in events:
    start = datetime.datetime.fromisoformat(event['start']['dateTime'])
    end = datetime.datetime.fromisoformat(event['end']['dateTime'])
    available_times.append((start, end))

# Print out the available times and ask the user to select one
for i, (start, end) in enumerate(available_times):
    print(f'{i+1}. {start.strftime("%Y-%m-%d %H:%M:%S")} - {end.strftime("%Y-%m-%d %H:%M:%S")}')

selected_time = int(input('Please select a meeting time by entering the corresponding number: '))

# Ask the user for any guests
guests = input('Please enter any guests (comma separated email addresses): ').split(',')

# Ask the user for a description
description = input('Please enter a description for the event: ')

# Create the event
event = {
    'summary': 'Meeting',
    'description': description,
    'start': {
        'dateTime': available_times[selected_time-1][0].isoformat(),
        'timeZone': 'UTC',
    },
    'end': {
        'dateTime': available_times[selected_time-1][1].isoformat(),
        'timeZone': 'UTC',
    },
    'attendees': [{'email': 'saucersam@gmail.com'}] + [{'email': guest} for guest in guests],
}

# Send the calendar invite
created_event = calendar_service.events().insert(calendarId='primary', body=event).execute()
print(f'Event created: {created_event.get("htmlLink")}')
