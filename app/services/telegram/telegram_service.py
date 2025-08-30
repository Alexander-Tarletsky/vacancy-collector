from sqlalchemy.ext.asyncio import AsyncSession
from telethon import events

from core.utils import SingletonMeta
from db import UserORM
from services.telegram.client_manager import TelegramClientManager


class TelegramService(metaclass=SingletonMeta):
    def __init__(self):
        self.manager = TelegramClientManager()
        self.user_sessions = {}

    async def start_for_user(self, user: UserORM, db_session: AsyncSession):
        await self.manager.init_client(user, db_session)

    async def stop_for_user(self, user_id: int):
        await self.manager.shutdown_client(user_id)

    async def update_channel_list(self, user_id: int):
        async with self.manager.lock:
            if user_id in self.manager.active_clients:
                client_data = self.manager.active_clients[user_id]
                client = client_data['client']
                client.remove_event_handler(self.manager.handle_new_message)
                client.add_event_handler(
                    self.manager.handle_new_message,
                    events.NewMessage(chats=self.manager.get_user_channels(user_id))
                )


# Singleton instance
telegram_service = TelegramService()
