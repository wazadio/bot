import asyncio
from telegram import Bot
from config import Config
from src.services import MemberService
from logs.logger import LOGGER as logger


class TelegramWorker:
    def __init__(self, config: Config, member_service: MemberService):
        self.bot = Bot(token=config.telegram_bot_token)
        self.group_id = config.telegram_group_id
        self.member_service = member_service

    def run_kick_task(self):
        """Synchronous wrapper for the async kick task"""
        try:
            asyncio.run(self.member_service.kick_non_members())
        except Exception as e:
            logger.error(f"Error running kick task: {e}")
