import aiosqlite
from enum import StrEnum
from typing import Optional

DB_PATH = "bot.db"

class SubscriptionType(StrEnum):
    ALL = "all"
    CITY = "city"
    GEO = "geo"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS subscriptions (
    user_id INTEGER PRIMARY KEY,
    sub_type TEXT NOT NULL,
    city TEXT,
    latitude REAL,
    longitude REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_TABLE_SQL)
        await db.commit()

async def upsert_subscription(user_id: int, sub_type: SubscriptionType, city: Optional[str] = None,
                              lat: Optional[float] = None, lon: Optional[float] = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "REPLACE INTO subscriptions (user_id, sub_type, city, latitude, longitude) VALUES (?, ?, ?, ?, ?)",
            (user_id, sub_type.value, city, lat, lon)
        )
        await db.commit()

async def remove_subscription(user_id: int, sub_type: SubscriptionType):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM subscriptions WHERE user_id = ? AND sub_type = ?",
            (user_id, sub_type.value)
        )
        await db.commit()

async def get_subscription(user_id: int, sub_type: SubscriptionType):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT city, latitude, longitude FROM subscriptions WHERE user_id = ? AND sub_type = ?",
            (user_id, sub_type.value)
        )
        return await cur.fetchone()

async def all_subscribers(sub_type: SubscriptionType):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT user_id, city, latitude, longitude FROM subscriptions WHERE sub_type = ?",
            (sub_type.value,)
        )
        return await cur.fetchall()
