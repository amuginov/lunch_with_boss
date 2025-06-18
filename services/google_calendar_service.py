from googleapiclient.discovery import build
from utils.google_auth import get_google_credentials

def create_event(summary, description, start_time, end_time, attendees):
    """
    Создаёт событие в Google Calendar.
    """
    print(f"Creating event in Google Calendar: Summary={summary}, Start={start_time}, End={end_time}, Attendees={attendees}")  # Отладочный вывод
    creds = get_google_credentials()
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_time, 'timeZone': 'UTC'},
        'end': {'dateTime': end_time, 'timeZone': 'UTC'},
        'attendees': [{'email': email} for email in attendees],
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created successfully: {created_event}")  # Отладочный вывод
    return created_event['id']

def delete_event(event_id):
    """
    Удаляет событие из Google Calendar.
    :param event_id: ID события.
    """
    creds = get_google_credentials()
    service = build('calendar', 'v3', credentials=creds)
    service.events().delete(calendarId='primary', eventId=event_id).execute()

def update_event(event_id, attendees):
    """
    Обновляет участников события.
    :param event_id: ID события.
    :param attendees: Список email участников.
    """
    creds = get_google_credentials()
    service = build('calendar', 'v3', credentials=creds)

    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    event['attendees'] = [{'email': email} for email in attendees]
    service.events().update(calendarId='primary', eventId=event_id, body=event).execute()