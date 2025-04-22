from aiogram import Router, types
from aiogram.filters import Command
from app.database.db import AsyncSessionLocal
from app.database.models import User

router = Router()

@router.message(Command("start"))
async def start_cmd(message: types.Message):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            user = User(tg_id=message.from_user.id)
            session.add(user)
            await session.commit()
    await message.answer("Добро пожаловать в OutletBot!")
