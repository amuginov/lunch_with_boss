from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar']

try:
    print("Проверяем файл credentials.json...")
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=8083)
    print("Файл credentials.json корректен.")
except Exception as e:
    print(f"Ошибка при чтении credentials.json: {e}")