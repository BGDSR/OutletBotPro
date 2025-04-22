from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.config import config  # Используем единый конфиг
import logging
from typing import AsyncGenerator

# Настройка логгирования
logger = logging.getLogger(__name__)

# Инициализация движка БД
engine = create_async_engine(
    config.DATABASE_URL,
    echo=False,  # В продакшене False, для отладки можно включить
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,   # Пересоздание соединений каждый час
    pool_size=20,        # Размер пула соединений
    max_overflow=10,     # Максимальное количество переполнений
    connect_args={
        "command_timeout": 60,  # Таймаут подключения 60 сек
        "server_settings": {
            "application_name": "telegram_bot"  # Идентификатор в PG
        }
    }
)

# Фабрика сессий с настройками
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Не истекать после коммита
    autoflush=False,
    future=True
)

Base = declarative_base()

async def create_db() -> None:
    """Создание всех таблиц в БД"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {e}")
        raise

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Генератор сессий для Dependency Injection"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            await session.close()

async def shutdown() -> None:
    """Корректное закрытие соединений при остановке"""
    logger.info("Closing database connections...")
    await engine.dispose()
    logger.info("Database connections closed")
