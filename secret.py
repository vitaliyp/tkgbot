import os

token = os.getenv("TELEGRAM_BOT_TOKEN", '')
forum = {
    'login': os.getenv('FORUM_LOGIN', ''),
    'password': os.getenv('FORUM_PASSWORD', '')
}
