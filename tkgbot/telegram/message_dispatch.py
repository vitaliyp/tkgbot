import enum
import threading

import aiohttp
import asyncio
import logging
from dataclasses import dataclass

from tkgbot import settings

logger = logging.getLogger(__name__)


class MessagePriority(enum.Enum):
    COMMAND = 1
    NOTIFICATION = 2


@dataclass
class TelegramMessage:
    chat_id: int
    text: str
    parse_mode: str = 'HTML'


@dataclass
class TelegramPhotoMessage(TelegramMessage):
    photo_url: str = ''


class TelegramSender:
    def __init__(self):
        self._session = aiohttp.ClientSession()

    async def _send_raw_message(self, method, data):
        logger.debug(f'Sending message: {data}.')
        async with self._session.post(settings.telegram_api_url + method, data=data) as resp:
            if resp.status != 200:
                try:
                    response_data = await resp.json()
                except ValueError as e:
                    response_data = {}
                logger.error(f'Error while sending message. Status: {resp.status}. Data: {response_data}.')

    async def send_message(self, message: TelegramMessage):
        if message.__class__ == TelegramMessage:
            payload = {
                'chat_id': message.chat_id,
                'text': message.text,
                'parse_mode': message.parse_mode,
                'disable_web_page_preview': True,
            }
            await self._send_raw_message('sendMessage', payload)
        elif isinstance(message, TelegramPhotoMessage):
            payload = {
                'chat_id': message.chat_id,
                'photo': message.photo_url,
                'parse_mode': message.parse_mode,
            }
            await self._send_raw_message('sendPhoto', payload)
        else:
            raise TypeError(f'Unknown message type: {type(message)}.')

    async def close(self):
        await self._session.close()


class MessageQueue:
    def __init__(self):
        self._queue = asyncio.PriorityQueue()
        self._message_id = 0
        self.lock = threading.Lock()

    def put_nowait(self, message: TelegramMessage, priority: MessagePriority):
        with self.lock:
            priority_tuple = (priority.value, self._message_id)
            self._queue.put_nowait((priority_tuple, message))
            self._message_id += 1

    async def put(self, message: TelegramMessage, priority: MessagePriority):
        with self.lock:
            priority_tuple = (priority.value, self._message_id)
            await self._queue.put((priority_tuple, message))
            self._message_id += 1

    async def get(self):
            priority, item = await self._queue.get()
            return item


class MessageWorker:
    """Gets message from the queue and sends them to intended clients"""
    def __init__(self, queue: MessageQueue, sender: TelegramSender):
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
