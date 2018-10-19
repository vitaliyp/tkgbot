import asyncio
import concurrent
import logging
from functools import partial

from tkgbot.telegram.message_dispatch import MessageWorker, TelegramSender
from . import job
from . import settings
from . import telegram
from .tkgbot import TkgBot


logger = logging.getLogger(__name__)


async def worker(application):
    bot = TkgBot()

    while True:
        try:
            messages = await telegram.get_messages()
            for message in messages:
                response = bot.process_request(message)
                if response:
                    await telegram.respond(response)
        except telegram.TelegramError:
            logger.warning(f'Error while getting messages from telegram', exc_info=True)
            await asyncio.sleep(5)


async def forum_check_scheduler(application):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=settings.thread_pool_executor_max_workers)
    loop = asyncio.get_event_loop()
    while True:
        logger.info('Checking forum for updates.')
        await loop.run_in_executor(executor, partial(job.run, application))
        await asyncio.sleep(settings.forum_check_interval)


def init_message_dispatch(application, loop: asyncio.AbstractEventLoop):
    message_queue = asyncio.Queue()
    sender = TelegramSender()
    message_worker = MessageWorker(message_queue, sender)
    task = loop.create_task(message_worker.run())

    application['messages_task'] = task
    application['messages_queue'] = message_queue


def run():
    application = {}

    logger = logging.getLogger(__name__)
    loop = asyncio.get_event_loop()
    init_message_dispatch(application, loop)
    loop.run_until_complete(asyncio.gather(
        worker(application),
        forum_check_scheduler(application)
    ))
    logger.info('Tearing down the application.')
