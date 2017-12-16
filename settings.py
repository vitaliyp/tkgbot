import gettext

import secret


PERSISTENCE_FILE = 'data.shelf'

translation = gettext.translation('tkgbot', './locales', languages=['uk'])

webhook_url = '/tkgbot/hooks/%s/'%secret.token
database_url = 'sqlite:///data.sqlite3'

debug = True
database_debug_output = debug
