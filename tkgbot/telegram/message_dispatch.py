import aiohttp
import asyncio
import logging
from dataclasses import dataclass

from tkgbot import settings

logger = logging.getLogger(__name__)


@dataclass
class TelegramMessage:
    chat_id: int
    text: str
    parse_mode: str = 'HTML'
    disable_web_page_preview: bool = True


class TelegramSender:
    def __init__(self):
        self._session = aiohttp.ClientSession()

    async def send_message(self, message: TelegramMessage):
        payload = {
            'chat_id': message.chat_id,
            'text': message.text,
            'parse_mode': message.parse_mode,
            'disable_web_page_preview': True,
        }
        logger.debug(f'Sending message: {payload}.')
        async with self._session.post(settings.telegram_api_url + 'sendMessage', data=payload) as resp:
            if resp.status != 200:
                try:
                    response_data = await resp.json()
                except ValueError as e:
                    response_data = {}
                logger.error(f'Error while sending message. Status: {resp.status}. Data: {response_data}.')

    async def close(self):
        await self._session.close()


class MessageWorker:
    """Gets message from the queue and sends them to intended clients"""
    def __init__(self, queue: asyncio.Queue, sender: TelegramSender):
        self.queue = queue
        self.sender = sender

    async def run(self):
        try:
            while True:
                message = await self.queue.get()
                await self.sender.send_message(message)
        except asyncio.CancelledError:
            return
        except Exception as e:
            logger.exception(f'Error while sending a message.')
