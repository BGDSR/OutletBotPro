from aiogram import Router, types
from aiogram.filters import Command  # Добавлен этот импорт
from app.database.db import AsyncSessionLocal
from app.database.models import User
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError  # Для обработки ошибок БД

router = Router()

@router.message(Command("start"))
async def start_cmd(message: types.Message):
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.tg_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()

            if not user:
                user = User(
                    tg_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name
                )
                session.add(user)
                await session.commit()
                await message.answer("Добро пожаловать в OutletBot! Вы зарегистрированы!")
            else:
                await message.answer("С возвращением в OutletBot!")

    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")
