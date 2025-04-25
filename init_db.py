# init_db.py
import asyncio
from app.database.db import db

async def main():
    db.init_engine()
    await db.create_tables()
    print("✅ Database initialized successfully")

if __name__ == "__main__":
    asyncio.run(main())
