import logging

from aiohttp import client

import settings
import secret

api_base_url = f'https://api.telegram.org/bot{secret.token}/'

async def remove_webhook():
    logger = logging.getLogger(__name__+'.remove_webhook')
    logger.info(f'Removing webhook.')
    async with client.ClientSession() as session:
        request_data = {'url': ''}
        response = await session.post(api_base_url+'deleteWebhook', data=request_data)
        response_data = await response.json()
        logger.debug(f'delete Webhook return result: {response_data}')
        if response_data['ok']:
            if response_data['result'] is True:
                logger.log('Webhook was deleted.')


offset = 0


async def get_updates(session):
    logger = logging.getLogger(__name__+'.get_updates')
    global offset

    request_data = {
        'timeout': settings.POLLING_TIMEOUT,
        'offset': offset,
    }
    response = await session.post(api_base_url+'getUpdates', data=request_data)
    response_data = await response.json()
    logger.debug(f'Received updates from server {response_data}')

    if response_data['result']:
        offset = response_data['result'][-1]['update_id']+1
        return response_data['result']
    return []


async def get_messages():
    with client.ClientSession() as session:
        while True:
            updates = await get_updates(session)
            if updates:
                messages = [update['message'] for update in updates if 'message' in update]
                return messages


async def respond(response):
    logger = logging.getLogger(__name__+'.respond')
    if not response['text']:
        return
    with client.ClientSession() as session:
        logger.debug(f'Sending message {response}')
        data = response
        async with session.post(api_base_url+'sendMessage', data=data) as response:
            response_data = await response.json()
            logger.debug(f'Response from server: {response_data}')
