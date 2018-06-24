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
forum_check_interval = 60

thread_pool_executor_max_workers = 3
