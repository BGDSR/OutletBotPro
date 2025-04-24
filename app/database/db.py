from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool
from app.config.config import config
import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class Database:
    """Класс для управления подключениями к БД"""
    
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._sessionmaker: Optional[async_sessionmaker] = None
        self.Base = declarative_base()

    def init_engine(self) -> None:
        """Инициализация асинхронного движка SQLAlchemy"""
        self._engine = create_async_engine(
            config.DATABASE_URL,
            echo=config.DEBUG,
            poolclass=NullPool if config.TESTING else None,
            pool_pre_ping=True,
            pool_size=20,
            max_overflow=10,
            pool_recycle=3600,
            connect_args={
                "command_timeout": 60,
                "server_settings": {
                    "application_name": "telegram_bot",
                    "statement_timeout": "30000"
                }
            }
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            future=True
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Асинхронный контекстный менеджер для сессий"""
        if not self._sessionmaker:
            raise RuntimeError("Database not initialized")
            
        session = self._sessionmaker()
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            await session.close()

    async def create_tables(self) -> None:
        """Создание всех таблиц"""
        if not self._engine:
            raise RuntimeError("Database not initialized")
            
        async with self._engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)
            logger.info("Database tables created")

    async def close(self) -> None:
        """Закрытие всех соединений"""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database connections closed")

# Инициализация глобального экземпляра
db = Database()
