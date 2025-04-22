from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from app.database.models import User
from app.database.db import get_session
from app.config import config
import logging
from typing import Annotated
from fastapi import Depends

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("start"))
async def start_cmd(
    message: types.Message,
    session: Annotated[AsyncSession, Depends(get_session)]  # Автоматическое управление сессией
):
    try:
        result = await session.execute(
            select(User).where(User.tg_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user:
            new_user = User(
                tg_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            session.add(new_user)
            await session.commit()
            await message.answer("✅ Добро пожаловать! Вы зарегистрированы!")
            logger.info(f"New user registered: {message.from_user.id}")
        else:
            await message.answer("👋 С возвращением!")
            logger.debug(f"Existing user: {message.from_user.id}")

    except SQLAlchemyError as e:
        logger.error(f"Database error in start_cmd: {e}")
        await message.answer("⚠️ Произошла ошибка. Попробуйте позже.")
        raise

@router.message(F.text == "Мой профиль")
async def profile_cmd(
    message: types.Message,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    try:
        result = await session.execute(
            select(User).where(User.tg_id == message.from_user.id)
        )
        user = result.scalar_one()
        
        await message.answer(
            f"📌 Ваш профиль:\n"
            f"ID: {user.tg_id}\n"
            f"Имя: {user.first_name}\n"
            f"Юзернейм: @{user.username}\n"
            f"Дата регистрации: {user.joined_at}"
        )
    except Exception as e:
        logger.error(f"Error in profile_cmd: {e}")
        await message.answer("❌ Ошибка загрузки профиля")
