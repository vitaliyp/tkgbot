import sys
import re

from bot import BotError, BotCommand, Bot
from models import Subscription, Node, NodeType
import database
from settings import translation


db_session = database.get_db_session()

_ = translation.gettext

MSG_INCORRECT_COMMAND=_('Incorrect command. Use /help for the list of commands.')
MSG_OK = _('Ok.')


def _parse_node_id(string):
    m = re.match('^((https?://)?(www.)?tkg.org.ua/node/)?(?P<node_id>\d+)$', string)
    if not m:
        return None
    node_id_str = m.group('node_id')
    try:
        node_id = int(node_id_str)
    except ValueError:
        return None
    return node_id


def _parse_node_type(string):
    choices = {
        'all': NodeType.ALL,
        'topics': NodeType.TOPIC,
        'materials': NodeType.MATERIAL,
        'events': NodeType.EVENT,
        'news': NodeType.NEWS
    }
    t = choices.get(string, None)
    return t.value if t else None


class SubscribeCommand(BotCommand):
    help = _(''' Subscribe
Usage: `/sub [node] [except|no-comments|no-replies]`
where node can be a link to forum topic or section or you can directly specify node id. Also you can use the next keywords:
    `all` - all updates on forum
    `events` - events on forum
    `materials` - materials on forum
    `news` - news
Options:
    `no-comments` - show only notifications about new topics
    `no-replies` - show only top-level comments
    `except` - disable all notifications from this node
Example:
    `/sub all`
    `/sub events except`
    `/sub 33044 except`
    `/sub 21303`
    `/sub tkg.org.ua/node/33044 no-comments`
    `/sub 33101 no-replies`''')

    def __call__(self, chat_id, args):
        args.reverse()
        if args:
            arg = args.pop().lower()
            node_type = _parse_node_type(arg)
            if node_type is not None:
                node_id = node_type
            else:
                node_id = _parse_node_id(arg)
            if node_id is None:
                return MSG_INCORRECT_COMMAND
        else:
            return MSG_INCORRECT_COMMAND

        exception = False
        no_comments = False
        no_replies = False
        if 'no-replies' in args:
            no_replies = True
            args.remove('no-replies')
        if 'no-comments' in args:
            no_comments = True
            no_replies = False
            args.remove('no-comments')
        if 'except' in args:
            exception = True
            no_comments = False
            no_replies = False
            args.remove('except')
        if args:
            return MSG_INCORRECT_COMMAND

        node = self.bot.session.query(Node).filter_by(id=node_id).first()
        if not node:
            node = Node(id=node_id)

        subscription = self.bot.session.query(Subscription).filter_by(node_id=node_id, chat_id=chat_id).first()
        if not subscription:
            subscription = Subscription(node=node, chat_id=chat_id)

        subscription.exception = exception
        subscription.no_comments = no_comments
        subscription.no_replies = no_replies

        self.bot.session.add(subscription)
        self.bot.session.commit()

        return MSG_OK


class HelpCommand:
    help = _('''Show this help message.''')

    def __call__(self, chat_id, args):
        if not self.bot:
            raise BotError('Command is not attached to any bot.')

        str_list = []
        for c_name, c in self.bot.commands.items():
            str_list.extend(('/', c_name))
            help_msg = getattr(c, 'help', None)
            if help_msg:
                lines = help_msg.expandtabs().splitlines()
                # Corrent docsting indentation
                min_indent = sys.maxsize
                for line in lines[1:]:
                    stripped = line.lstrip()
                    if stripped:
                        min_indent = min(min_indent, len(line)-len(stripped))
                trimmed = [lines[0].strip()]
                if min_indent<sys.maxsize:
                    for line in lines[1:]:
                        trimmed.append(line[min_indent:].rstrip())
                str_list.extend((' - ', '\n'.join(trimmed)))
            str_list.append('\n')
        return ''.join(str_list)


class UnsubscribeCommand(BotCommand):
    help = _('''Unsubscribe''')

    def __call__(self, chat_id, args):
        args.reverse()
        if args:
            arg = args.pop().lower()
            node_type = _parse_node_type(arg)
            if node_type is not None:
                node_id = node_type
            else:
                node_id = _parse_node_id(arg)
            if node_id is None:
                return MSG_INCORRECT_COMMAND
        else:
            return MSG_INCORRECT_COMMAND

        self.bot.session.query(Subscription).filter_by(node_id=node_id, chat_id=chat_id).delete()
        self.bot.session.commit()

        return MSG_OK


class UnsubscribeFromAllCommand(BotCommand):
    help = _('''Remove all subscriptions''')

    def __call__(self, chat_id, args):
        self.bot.session.query(Subscription).filter_by(chat_id=chat_id).delete()
        self.bot.session.commit()
        return MSG_OK


class ShowCommand(BotCommand):
    help = _('''Show your subscriptions''')

    def __call__(self, chat_id, args):
        subs = self.bot.session.query(Subscription).filter_by(chat_id=chat_id).all()

        if not subs:
            return _('You have no subscriptions')

        msg_list = []
        node_strs = {
            NodeType.ALL: 'all',
            NodeType.MATERIAL: 'materials',
            NodeType.EVENT: 'events',
            NodeType.TOPIC: 'topics',
            NodeType.NEWS: 'news',
        }

        for sub in subs:
            sub_list = []
            try:
                t = NodeType(sub.node_id)
                node_name = node_strs.get(t, str(sub.node_id))
            except ValueError:
                node_name = str(sub.node_id)
            sub_list.append('*'+node_name+'*')
            if sub.exception:
                sub_list.append('except')
            if sub.no_comments:
                sub_list.append('no-comments')
            if sub.no_replies:
                sub_list.append('no-replies')
            if sub.node.name:
                sub_list.append('('+sub.node.name+')')
            msg_list.append(' '.join(sub_list))

        return '\n'.join(msg_list)


class WrongCommand(BotCommand):
    def __call__(self, chat_id, args):
        return MSG_INCORRECT_COMMAND


class TkgBot(Bot):
    def __init__(self):
        super().__init__()

        self.add_command('show', ShowCommand())
        self.add_command('sub', SubscribeCommand())
        self.add_command('unsub', UnsubscribeCommand())
        self.add_command('unsuball', UnsubscribeFromAllCommand())
        self.add_command('help', HelpCommand())

        self.set_default_command(WrongCommand())

