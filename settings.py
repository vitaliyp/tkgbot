import gettext
import logging

logging.basicConfig(level=logging.DEBUG)


translation = gettext.translation('tkgbot', './locales', languages=['uk'])

database_url = 'sqlite:///data/data.sqlite3'

debug = True
database_debug_output = debug

POLLING_TIMEOUT = 300
FORUM_CHECK_INTERVAL = 60

THREAD_POOL_EXECUTOR_MAX_WORKERS = 3
