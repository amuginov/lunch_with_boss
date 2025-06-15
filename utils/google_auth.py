import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Укажите доступы, необходимые для работы с Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_google_credentials():
    """
    Получает учетные данные для работы с Google API.
    """
    creds = None
    # Проверяем, есть ли сохранённые токены
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Если токенов нет или они устарели, запускаем процесс авторизации
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Сохраняем токены в файл
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds