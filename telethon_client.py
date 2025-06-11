from telethon import TelegramClient

api_id = 24084625  # свой id
api_hash = 'ac64a9e662993d9082004e6521650ee7'

with TelegramClient('anon', api_id, api_hash) as client:
    print('Session created!')