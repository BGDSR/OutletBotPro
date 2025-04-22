from aiogram import Router, types
from aiogram.filters import Command
from app.config import ADMIN_IDS
from app.database.db import AsyncSessionLocal
from sqlalchemy import select
from app.database.models import User
import logging

router = Router()
logger = logging.getLogger(__name__)

if not ADMIN_IDS:
    logger.error("ADMIN_IDS не заданы в .env")
    raise ValueError("ADMIN_IDS не заданы в .env")

@router.message(Command("stats"))
async def stats_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("Нет доступа.")
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
        await message.answer(f"Всего пользователей: {len(users)}")
    except Exception as e:
        logger.error(f"Ошибка в stats_cmd: {e}")
        await message.answer("Произошла ошибка при получении статистики")
