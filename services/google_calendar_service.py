from googleapiclient.discovery import build
from utils.google_auth import get_google_credentials

def create_event(summary, description, start_time, end_time, attendees):
    """
    Создаёт событие в Google Calendar.
    :param summary: Название события.
    :param description: Описание события.
    :param start_time: Время начала (ISO 8601).
    :param end_time: Время окончания (ISO 8601).
    :param attendees: Список email участников.
    :return: ID созданного события.
    """
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