from sqlalchemy import Column, Integer, BigInteger, DateTime
from sqlalchemy.sql import func
from app.database.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True, index=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    class User(Base):
    # ... существующие поля ...
    is_active = Column(Boolean, default=True)  # Для управления рассылками
