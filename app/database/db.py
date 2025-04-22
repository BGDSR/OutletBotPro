from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

# Удалите дублирование engine! Оставьте только этот вариант:
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Включите для отладки, в продакшене False
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=20,
    max_overflow=10
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
