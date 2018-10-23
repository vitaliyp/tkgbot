import asyncio
from asyncio import Queue

import pytest
from tkgbot import testutils

from tkgbot.telegram.message_dispatch import TelegramSender, MessageWorker, TelegramMessage, MessagePriority
from tkgbot.telegram import message_dispatch


@pytest.mark.asyncio
async def test_worker():
    sender = TelegramSender()
    sender.send_message = testutils.get_mock_coro()

    queue = message_dispatch.MessageQueue()
    worker = MessageWorker(queue, sender)

    message = TelegramMessage(123, 'test')

    loop = asyncio.get_event_loop()
    task: asyncio.Task = loop.create_task(worker.run())

    await queue.put(message, MessagePriority.NOTIFICATION)
    await asyncio.sleep(0.1)

    task.cancel()

    sender.send_message.assert_called_once_with(message)
