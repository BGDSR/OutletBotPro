from aiogram import Router, types
from app.config import ADMIN_IDS
from app.database.db import AsyncSessionLocal
from sqlalchemy import select
from app.database.models import User

router = Router()

@router.message(commands=["stats"])
async def stats_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("Нет доступа.")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
    await message.answer(f"Всего пользователей: {len(users)}")