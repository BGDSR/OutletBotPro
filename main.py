from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage  # Изменено!
from app.handlers import user, admin
from app.database.db import create_db
import asyncio
import logging
from app.config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        # Инициализация Redis для FSM и кеша
        storage = RedisStorage.from_url("redis://localhost:6379/0")
        
        bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
        dp = Dispatcher(storage=storage)

        dp.include_router(user.router)
        dp.include_router(admin.router)

        await create_db()
        logger.info("Бот запущен")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Ошибка запуска: {e}")

if __name__ == "__main__":
    asyncio.run(main())
