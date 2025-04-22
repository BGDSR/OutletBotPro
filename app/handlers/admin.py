from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session  # или ваш путь к функции get_session
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from app.database.models import User
from app.database.db import get_session
from app.config import config
import logging
from typing import Annotated
from fastapi import Depends

router = Router()
logger = logging.getLogger(__name__)

if not config.ADMIN_IDS:
    logger.critical("ADMIN_IDS not configured!")
    raise ValueError("ADMIN_IDS not set in config")

@router.message(Command("stats"))
async def stats_cmd(
    message: types.Message,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    if message.from_user.id not in config.ADMIN_IDS:
        logger.warning(f"Unauthorized access attempt by {message.from_user.id}")
        return await message.answer("⛔ Нет доступа!")

    try:
        # Получаем общее количество пользователей
        total_users = await session.scalar(select(func.count(User.id)))
        
        # Получаем последних 5 пользователей
        last_users = await session.execute(
            select(User)
            .order_by(User.joined_at.desc())
            .limit(5)
        )
        
        response = [
            f"📊 Статистика:",
            f"• Всего пользователей: {total_users}",
            f"• Последние регистрации:"
        ]
        
        for user in last_users.scalars():
            response.append(f"  - {user.first_name} (@{user.username}) [{user.joined_at.date()}]")
        
        await message.answer("\n".join(response))
        logger.info(f"Admin stats requested by {message.from_user.id}")

    except SQLAlchemyError as e:
        logger.error(f"Database error in stats_cmd: {e}")
        await message.answer("⚠️ Ошибка получения статистики")
        raise

@router.message(Command("broadcast"))
async def broadcast_cmd(
    message: types.Message,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    if message.from_user.id not in config.ADMIN_IDS:
        return await message.answer("⛔ Нет доступа!")

    # Проверяем есть ли текст после команды
    if not message.text.split(maxsplit=1)[1:]:
        return await message.answer("ℹ️ Использование: /broadcast текст")
    
    broadcast_text = message.text.split(maxsplit=1)[1]
    
    try:
        users = await session.scalars(select(User.tg_id))
        count = 0
        
        for user_id in users:
            try:
                await message.bot.send_message(user_id, broadcast_text)
                count += 1
            except Exception as e:
                logger.warning(f"Can't send to {user_id}: {e}")
        
        await message.answer(f"📣 Рассылка завершена! Отправлено {count} пользователям.")
        logger.info(f"Broadcast sent to {count} users by admin {message.from_user.id}")

    except SQLAlchemyError as e:
        logger.error(f"Broadcast error: {e}")
        await message.answer("⚠️ Ошибка при рассылке")
