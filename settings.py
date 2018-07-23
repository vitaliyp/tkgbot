import os
import gettext
import logging

import secret

logging.basicConfig(level=logging.DEBUG)


translation = gettext.translation('tkgbot', './locales', languages=['uk'])

database_url = 'sqlite:///data/data.sqlite3'

debug = True
database_debug_output = debug

telegram_api_url = f'https://api.telegram.org/bot{secret.token}/'
polling_timeout = 300

try:
    forum_check_interval = int(os.getenv('FORUM_CHECK_INTERVAL', 'not-an-int'))
except ValueError:
    forum_check_interval = 600

thread_pool_executor_max_workers = 3
