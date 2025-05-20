from fastapi import FastAPI
from api.routers import users

# Создаем FastAPI-приложение
app = FastAPI()

# Подключаем роуты
app.include_router(users.router)
