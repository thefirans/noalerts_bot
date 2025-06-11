from telethon import TelegramClient, events
import asyncio

api_id = 24084625  # замени
api_hash = 'ac64a9e662993d9082004e6521650ee7'
session_name = 'anon'  # файл, что создал ранее

CHANNELS = ['war_monitor', 'radar_raketaa', 'vanek_nikolaev']

# Место для хранения ID подписчиков сводки
general_subscribers = set()

client = TelegramClient(session_name, api_id, api_hash)

async def telethon_worker(send_func):
    @client.on(events.NewMessage(chats=CHANNELS))
    async def handler(event):
        message = event.message.message
        for user_id in general_subscribers:
            await send_func(user_id, f"🛡️ Сводка: {message}")

    await client.start()
    await client.run_until_disconnected()