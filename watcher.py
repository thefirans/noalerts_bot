import os
import asyncio
import time
from telethon import TelegramClient, events
from db import SubscriptionType, all_subscribers
from relevance import is_relevant

API_ID = int(os.getenv("TG_API_ID", "0"))
API_HASH = os.getenv("TG_API_HASH", "")
SESSION_NAME = os.getenv("TG_SESSION", "anon")

CHANNELS_FILE = "channels.txt"  # each line is a channel username

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

recent = {}
DEDUP_INTERVAL = 3600

async def load_channels():
    try:
        with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

async def start(bot_send_func):
    channels = await load_channels()

    @client.on(events.NewMessage(chats=channels))
    async def handler(event):
        message_text = event.message.message
        now = time.time()
        h = hash(message_text)
        if h in recent and now - recent[h] < DEDUP_INTERVAL:
            return
        recent[h] = now
        # purge old hashes
        for key, ts in list(recent.items()):
            if now - ts > DEDUP_INTERVAL:
                recent.pop(key, None)
        # national subscribers
        subs = await all_subscribers(SubscriptionType.ALL)
        for user_id, *_ in subs:
            await bot_send_func(user_id, message_text)
        # city subscribers
        city_subs = await all_subscribers(SubscriptionType.CITY)
        for user_id, city, *_ in city_subs:
            if await is_relevant(message_text, city):
                await bot_send_func(user_id, message_text)
        # geo subscribers (stored as city after reverse geocode)
        geo_subs = await all_subscribers(SubscriptionType.GEO)
        for user_id, city, *_ in geo_subs:
            if await is_relevant(message_text, city):
                await bot_send_func(user_id, message_text)

    await client.start()
    await client.run_until_disconnected()
