# from telethon import TelegramClient
# from telethon.sessions import SQLiteSession


class TelegramService:
    pass


import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from telethon import TelegramClient, events

from db.connect import get_session
from db.models import UserORM
from schemas.vacancy import VacancyCreate

router = APIRouter()
logger = logging.getLogger("telegram_service")

TELEGRAM_API_ID = 28180629
TELEGRAM_API_HASH = "f7e3be997d8d2408c8e58769b428bfb3"
WEBHOOK_URL = "your_webhook_url"

clients = {}

def get_telegram_client(user_id: str, api_id: int, api_hash: str):
    if user_id not in clients:
        clients[user_id] = TelegramClient(f"session_{user_id}", api_id, api_hash)
    return clients[user_id]

async def start_client(user: UserORM):
    client = get_telegram_client(str(user.id), TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await client.start()
    logger.info(f"Telegram client started for user {user.id}")

    @client.on(events.NewMessage)
    async def handle_new_message(event):
        logger.info(f"New message received: {event.raw_text}")
        async with AsyncSession() as db_session:
            vacancy_data = VacancyCreate(
                channel_id=event.chat_id,
                title=event.raw_text[:100],
                description=event.raw_text,
                is_opportunity=False,
                contact="",
                is_applied=False,
                is_rejected=False,
            )
            await create_vacancy(db, vacancy_data)

    await client.run_until_disconnected()

@router.post("/telegram/start")
async def start_telegram(user: UserORM = Depends(get_current_user), db_session: AsyncSession = Depends(get_session)):
    await start_client(user)
    return {"message": "Telegram client started"}

@router.get("/telegram/channels")
async def list_channels(user: UserORM = Depends(get_current_user), db_session: AsyncSession = Depends(get_session)):
    return await get_user_channels(db, user.id)

@router.post("/telegram/webhook")
async def receive_update(request: Request):
    data = await request.json()
    logger.info(f"Received Telegram update: {data}")
    return {"message": "Update received"}
