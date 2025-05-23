from .help import router as help_router
from .start import router as start_router

# Объединяем роутеры в один
from aiogram import Router

router = Router()
router.include_router(help_router)
router.include_router(start_router)