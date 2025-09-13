"""
Workers module for handling business logic in separate processes/threads.

This module contains worker classes that handle specific business operations
for the Telegram bot, allowing for better separation of concerns and scalability.
"""

from .telegram import TelegramWorker
from .scheduler import Scheduler

__all__ = ['TelegramWorker', 'Scheduler']
