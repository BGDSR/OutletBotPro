import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from app.config.config import config
from app.database.db import create_db, shutdown_db
from app.handlers import user_router, admin_router
from app.middlewares import register_middlewares

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def on_startup():
    """Действия при запуске бота"""
    try:
        logger.info("Initializing database...")
        await create_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def on_shutdown():
    """Действия при остановке бота"""
    try:
        logger.info("Shutting down...")
        await shutdown_db()
        logger.info("Bot shutdown completed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

async def setup_dispatcher(dp: Dispatcher):
    """Настройка диспетчера"""
    # Регистрация middleware
    register_middlewares(dp)
    
    # Подключение роутеров
    dp.include_router(admin_router)
    dp.include_router(user_router)
    
    # События запуска/остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

async def main():
    """Основная функция запуска бота"""
    try:
        # Инициализация хранилища и бота
        storage = RedisStorage.from_url(config.REDIS_URL)
        bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
        dp = Dispatcher(storage=storage)
        
        # Настройка диспетчера
        await setup_dispatcher(dp)

        logger.info("Starting bot in polling mode...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
    finally:
        await on_shutdown()

if __name__ == "__main__":
    # Настройка обработки сигналов для корректного завершения
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
