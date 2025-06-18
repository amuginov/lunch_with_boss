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
        'start': {'dateTime': start_time, 'timeZone': 'Europe/Moscow'},  # Указываем часовой пояс
        'end': {'dateTime': end_time, 'timeZone': 'Europe/Moscow'},      # Указываем часовой пояс
        'attendees': [{'email': email} for email in attendees],
    }

    created_event = service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()
    print(f"Event created successfully: {created_event}")  # Отладочный вывод
    return created_event['id']

def delete_event(event_id):
    """
    Удаляет событие из Google Calendar.
    :param event_id: ID события.
    """
    try:
        creds = get_google_credentials()
        service = build('calendar', 'v3', credentials=creds)
        print(f"Attempting to delete event with ID: {event_id}")  # Отладочный вывод
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print(f"Event with ID {event_id} deleted successfully.")  # Отладочный вывод
    except Exception as e:
        print(f"Error while deleting event with ID {event_id}: {e}")  # Отладочный вывод
        raise Exception(f"Ошибка при удалении события из Google Calendar: {e}")

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