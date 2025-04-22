from aiogram import Router, types
from app.database.db import AsyncSessionLocal
from app.database.models import User
from sqlalchemy import select

router = Router()

@router.message(Command("start"))
async def start_cmd(message: types.Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.tg_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user:
            user = User(tg_id=message.from_user.id)
            session.add(user)
            await session.commit()

    await message.answer("Добро пожаловать в OutletBot!")
