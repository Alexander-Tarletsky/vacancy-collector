import asyncio
import logging

from telethon import TelegramClient, events
from telethon.sessions import SQLiteSession

from crud.channel import channel_crud
from crud.vacancy import vacancy_crud
from db.connect import AsyncSession
from db.models import UserORM

logger = logging.getLogger(__name__)


class TelegramClientManager:
    def __init__(self):
        self.active_clients = {}
        self.lock = asyncio.Lock()

    async def init_client(self, user: UserORM, db_session: AsyncSession):
        async with self.lock:
            if user.id not in self.active_clients:
                session = SQLiteSession(f"user_{user.id}")
                client = TelegramClient(
                    session,
                    user.api_id,
                    user.api_hash,
                    base_logger=logger
                )

                await client.start()
                self.active_clients[user.id] = {
                    'client': client,
                    'db': db_session,
                    'user': user
                }

                # Add event handlers
                client.add_event_handler(
                    self.handle_new_message,
                    events.NewMessage(chats=self.get_user_channels(user.id))
                )

                asyncio.create_task(client.run_until_disconnected())
                logger.info(f"Started client for user {user.id}")

    async def shutdown_client(self, user_id: int):
        async with self.lock:
            if user_id in self.active_clients:
                client = self.active_clients[user_id]['client']
                await client.disconnect()
                del self.active_clients[user_id]
                logger.info(f"Stopped client for user {user_id}")

    def get_user_channels(self, user_id: int):
        # Get active channels from database
        return asyncio.run(
            channel_crud.get_active_channels(self.active_clients[user_id]['db'], user_id)
        )

    async def handle_new_message(self, event):
        user_id = event.client.session.user_id
        async with AsyncSession() as db_session:
            vacancy_data = {
                'message_id': event.message.id,
                'content': event.message.text,
                'channel_id': event.chat_id
            }
            await vacancy_crud.create(db_session, vacancy_data)
