from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from app.handlers import user, admin
from app.database.db import create_db, shutdown  # Добавлен shutdown
import asyncio
import logging
from app.config import config  # Используем объект config вместо прямой загрузки

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),  # Логи в файл
        logging.StreamHandler()         # Логи в консоль
    ]
)
logger = logging.getLogger(__name__)

async def on_startup():
    """Действия при запуске бота"""
    logger.info("Starting bot...")
    await create_db()

async def on_shutdown():
    """Действия при остановке бота"""
    logger.info("Shutting down...")
    await shutdown()  # Корректное закрытие соединений

async def main():
    try:
        # Инициализация Redis
        storage = RedisStorage.from_url(config.REDIS_URL)
        
        bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
        dp = Dispatcher(storage=storage)

        # Регистрация роутеров
        dp.include_router(user.router)
        dp.include_router(admin.router)

        # События запуска/остановки
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        logger.info("Bot started successfully")
        await dp.start_polling(bot)

    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
