from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
import asyncio
import logging
from app.config.config import config
from app.database.db import create_db, shutdown
from app.handlers import user_router, admin_router  # Изменён импорт

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    try:
        storage = RedisStorage.from_url(config.REDIS_URL)
        bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
        dp = Dispatcher(storage=storage)

        dp.include_router(admin_router)
        dp.include_router(user_router)

        await create_db()
        logger.info("Bot started")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Failed to start: {e}")
    finally:
        await shutdown()

if __name__ == "__main__":
    asyncio.run(main())
