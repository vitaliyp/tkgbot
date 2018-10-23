import logging

import aiohttp
from aiohttp import client

from tkgbot import settings
from tkgbot.settings import telegram_api_url

logger = logging.getLogger(__name__)


class TelegramError(Exception):
    pass


async def remove_webhook():
    logger.info(f'Removing webhook.')
    async with client.ClientSession() as session:
        request_data = {'url': ''}
        response = await session.post(telegram_api_url + 'deleteWebhook', data=request_data)
        response_data = await response.json()
        logger.debug(f'delete Webhook return result: {response_data}')
        if response_data['ok']:
            if response_data['result'] is True:
                logger.info('Webhook was deleted.')


offset = 0


async def get_updates(session):
    global offset

    request_data = {
        'timeout': settings.polling_timeout,
        'offset': offset,
    }
    try:
        response = await session.post(telegram_api_url + 'getUpdates', data=request_data)
        response_data = await response.json()
    except aiohttp.client_exceptions.ClientError as error:
        raise TelegramError from error

    logger.debug(f'Received updates from Telegram {response_data}')

    if not response_data.get('ok'):
        error_code = response_data.get('error_code')
        description = response_data.get('description')
        raise TelegramError(f'{error_code} {description}')

    if response_data['result']:
        offset = response_data['result'][-1]['update_id']+1
        return response_data['result']

    return []


async def get_messages():
    async with client.ClientSession() as session:
        while True:
            updates = await get_updates(session)
            if updates:
                messages = [update['message'] for update in updates if 'message' in update]
                return messages
