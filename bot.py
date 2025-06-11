import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram import types
from aiogram.filters import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from db import (
    init_db,
    SubscriptionType,
    upsert_subscription,
    remove_subscription,
    get_subscription,
)
from geo_utils import resolve_city, reverse_geocode, suggest_cities
from watcher import start as start_watcher

API_TOKEN = os.getenv("TG_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(API_TOKEN)
dp = Dispatcher()

ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x}
CHANNELS_FILE = "channels.txt"

start_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Send Location", request_location=True)]],
    resize_keyboard=True,
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Welcome! Use /subscribe_all, /subscribe_city <city>, or share your location.",
        reply_markup=start_kb,
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "/subscribe_all, /unsubscribe_all, /subscribe_city <city>, /unsubscribe_city, /unsubscribe_geo, /my_settings."
    )

@dp.message(Command("subscribe_all"))
async def subscribe_all(message: types.Message):
    await upsert_subscription(message.from_user.id, SubscriptionType.ALL)
    await message.answer("Subscribed to national alerts.")

@dp.message(Command("unsubscribe_all"))
async def unsubscribe_all(message: types.Message):
    await remove_subscription(message.from_user.id, SubscriptionType.ALL)
    await message.answer("Unsubscribed from national alerts.")

@dp.message(Command("subscribe_city"))
async def subscribe_city(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Please provide a city name.")
        return
    city = await resolve_city(parts[1])
    if not city:
        suggestions = suggest_cities(parts[1])
        if suggestions:
            await message.answer(
                "City not found. Did you mean: " + ", ".join(suggestions)
            )
        else:
            await message.answer("City not found in Ukraine.")
        return
    await upsert_subscription(message.from_user.id, SubscriptionType.CITY, city=city)
    await message.answer(f"Subscribed to alerts for {city}.")

@dp.message(Command("unsubscribe_city"))
async def unsubscribe_city(message: types.Message):
    await remove_subscription(message.from_user.id, SubscriptionType.CITY)
    await message.answer("Unsubscribed from city alerts.")


@dp.message(Command("add_channel"))
async def add_channel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /add_channel <username>")
        return
    with open(CHANNELS_FILE, "a", encoding="utf-8") as f:
        f.write(parts[1].strip() + "\n")
    await message.answer("Channel added. Restart bot to apply.")


@dp.message(Command("remove_channel"))
async def remove_channel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /remove_channel <username>")
        return
    try:
        with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f]
        lines = [l for l in lines if l != parts[1].strip()]
        with open(CHANNELS_FILE, "w", encoding="utf-8") as f:
            for l in lines:
                f.write(l + "\n")
        await message.answer("Channel removed. Restart bot to apply.")
    except FileNotFoundError:
        await message.answer("Channels file missing.")

@dp.message(Command("unsubscribe_geo"))
async def unsubscribe_geo(message: types.Message):
    await remove_subscription(message.from_user.id, SubscriptionType.GEO)
    await message.answer("Geolocation subscription removed.")

@dp.message(Command("my_settings"))
async def my_settings(message: types.Message):
    parts = []
    for sub in [SubscriptionType.ALL, SubscriptionType.CITY, SubscriptionType.GEO]:
        res = await get_subscription(message.from_user.id, sub)
        if res:
            parts.append(f"{sub.value}: {res[0] if res[0] else ''}")
    await message.answer("; ".join(parts) if parts else "No subscriptions")

@dp.message(lambda m: m.location is not None)
async def handle_location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude
    city = await reverse_geocode(lat, lon)
    if not city:
        await message.answer("Could not determine nearest city.")
        return
    await upsert_subscription(message.from_user.id, SubscriptionType.GEO, city=city, lat=lat, lon=lon)
    await message.answer(f"Subscribed by location: {city}")

async def main():
    await init_db()
    watcher_task = asyncio.create_task(start_watcher(lambda uid, text: bot.send_message(uid, text)))
    try:
        await dp.start_polling(bot)
    finally:
        watcher_task.cancel()
        await watcher_task

if __name__ == "__main__":
    asyncio.run(main())
