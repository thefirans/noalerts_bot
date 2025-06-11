from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio

# Вставь свой токен бота сюда
API_TOKEN = "7708298003:AAG_tItRzlQQp7sg1SehhzarqcLtg1s1LFw"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привіт! Я бот для оповіщень про тривоги. Обери місто або поділись геолокацією, щоб отримувати персоналізовані сповіщення.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())