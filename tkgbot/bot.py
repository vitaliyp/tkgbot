from . import database


class BotError(Exception):
    pass


class Bot:
    def __init__(self):
        self.commands = {}
        self.default_command = None
        self.session = None

    def add_command(self, command_name, command):
        self.commands[command_name] = command
        command.bot = self

    def set_default_command(self, command):
        self.default_command = command
        command.bot = self

    def _find_command(self, command_name):
        if command_name in self.commands:
            return self.commands[command_name]

        if self.default_command:
            return self.default_command

        return None

    def process_request(self, message):
        if 'text' not in message:
            return None

        with database.session_scope() as session:
            self.session = session

            message_text = message['text']
            chat_id = message['chat']['id']

            message_list = message_text.split()
            if message_list[0].startswith('/'):
                command_name = message_list[0][1:]
                command = self._find_command(command_name)
                args = message_list[1:]
                if command:
                    return_message = command(chat_id, args)
                else:
                    return None
            else:
                return_message = self.default_command(chat_id, [])

            response = {
                'chat_id': chat_id,
                'text': return_message,
                'parse_mode': 'markdown',
            }

            self.session = None

        return response


class BotCommand:
    def __init__(self):
        self.bot = None

    def __call__(self, chat_id, args):
        raise NotImplementedError
