import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    @property
    def BOT_TOKEN(self):
        token = os.getenv("BOT_TOKEN")
        if not token:
            logger.error("BOT_TOKEN не задан в .env")
            raise ValueError("BOT_TOKEN не задан")
        return token

    @property
    def DATABASE_URL(self):
        url = os.getenv("DATABASE_URL")
        if not url:
            logger.error("DATABASE_URL не задан в .env")
            raise ValueError("DATABASE_URL не задан")
        return url

    @property
    def REDIS_URL(self):
        url = os.getenv("REDIS_URL")
        if not url:
            logger.error("REDIS_URL не задан в .env")
            raise ValueError("REDIS_URL не задан")
        return url

    @property
    def ADMIN_IDS(self):
        ids = os.getenv("ADMIN_IDS", "")
        return [int(i) for i in ids.split(",")] if ids else []

config = Config()
