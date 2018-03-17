import asyncio
import concurrent
import logging

import job
import settings
import telegram
from tkgbot import TkgBot


logger = logging.getLogger(__name__)


async def worker():
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


async def forum_check_scheduler():
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=settings.THREAD_POOL_EXECUTOR_MAX_WORKERS)
    loop = asyncio.get_event_loop()
    while True:
        logger.info('Checking forum for updates.')
        await loop.run_in_executor(executor, job.run)
        await asyncio.sleep(settings.FORUM_CHECK_INTERVAL)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(
        worker(),
        forum_check_scheduler()
    ))
    logger.info('Tearing down the application.')
