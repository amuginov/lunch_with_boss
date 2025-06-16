import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Укажите доступы, необходимые для работы с Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

print("Скрипт запущен.")

def get_google_credentials():
    """
    Получает учетные данные для работы с Google API.
    """
    print("Начало работы функции get_google_credentials.")
    creds = None
    # Проверяем, есть ли сохранённые токены
    print("Проверяем наличие token.json...")
    if os.path.exists('token.json'):
        print("Файл token.json найден.")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        print("Токен успешно загружен из token.json.")
    else:
        print("Файл token.json не найден. Запускаем авторизацию...")
    # Если токенов нет или они устарели, запускаем процесс авторизации
    if not creds or not creds.valid:
        print("Токен отсутствует или недействителен.")
        if creds and creds.expired and creds.refresh_token:
            print("Токен истёк. Обновляем токен...")
            creds.refresh(Request())
            print("Токен успешно обновлён.")
        else:
            print("Начало авторизации...")
            try:
                print("Проверяем файл credentials.json...")
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                print("Файл credentials.json корректен.")
                print("Создан объект flow.")
                print("Попытка запустить консоль для авторизации...")
                auth_url, _ = flow.authorization_url(prompt='consent')
                print(f"Откройте эту ссылку в браузере: {auth_url}")
                creds = flow.run_console()
                print("Авторизация завершена.")
            except Exception as e:
                print(f"Ошибка при чтении credentials.json: {e}")
                print(f"Ошибка при запуске консоли: {e}")
        # Сохраняем токены в файл
        if creds:
            print("Сохраняем токен в файл token.json...")
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            print("Токен успешно сохранён.")
    print("Завершение работы функции get_google_credentials.")
    return creds

if __name__ == "__main__":
    get_google_credentials()