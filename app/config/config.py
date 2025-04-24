import os
from dotenv import load_dotenv
import logging
from typing import List, Optional
from pydantic import BaseSettings, validator, RedisDsn, PostgresDsn

# Настройка логгера перед загрузкой конфига
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Класс конфигурации с валидацией и типами"""
    
    # Основные настройки
    BOT_TOKEN: str
    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn
    ADMIN_IDS: List[int] = []
    DEBUG: bool = False
    
    # Валидаторы
    @validator('BOT_TOKEN')
    def validate_bot_token(cls, v):
        if not v.startswith('5'):
            logger.error('Неверный формат BOT_TOKEN')
            raise ValueError('Invalid BOT_TOKEN format')
        return v
    
    @validator('ADMIN_IDS', pre=True)
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(i.strip()) for i in v.split(',') if i.strip()]
        return v or []

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True

def load_config() -> Settings:
    """Загрузка конфигурации с обработкой ошибок"""
    try:
        load_dotenv()
        return Settings()
    except Exception as e:
        logger.critical(f'Ошибка загрузки конфигурации: {e}')
        raise

config = load_config()
