import sys
import re

from bot import BotError, BotCommand, Bot
from models import Subscription, Node, NodeType
from settings import translation


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
        def get_node_description(node_id):
            node_descriptions = {
                NodeType.ALL: _('Whole forum'),
                NodeType.MATERIAL: _('Materials'),
                NodeType.EVENT: _('Events'),
                NodeType.TOPIC: _('Topics'),
                NodeType.NEWS: _('News'),
            }

            try:
                result = node_descriptions.get(NodeType(node_id), '')
            except ValueError:
                result = ''

            return result

        def get_node_str(node_id):
            node_strs = {
                NodeType.ALL: 'all',
                NodeType.MATERIAL: 'materials',
                NodeType.EVENT: 'events',
                NodeType.TOPIC: 'topics',
                NodeType.NEWS: 'news',
            }
            
            try:
                result = node_strs.get(NodeType(node_id), '')
            except ValueError:
                result = ''

            return result

        def build_subscription_info(sub):
            line = ['  -'] # What are you looking at?

            node_description = get_node_description(sub.node_id)
            if node_description:
                line.append(f' {node_description}')
            elif sub.node.name and sub.node.name:
                line.append(f' "{sub.node.name}"')

            if not sub.exception:
                if sub.no_replies or sub.no_comments:
                    line.append(' (')

                    param_str = []
                    if sub.no_replies:
                        param_str.append(_('top level posts only'))
                    if sub.no_comments:
                        param_str.append(_('without comments'))
                    line.append(', '.join(param_str))
                    
                    line.append(')')
            if not node_description:
                line.append(f' \[`{sub.node_id}`]')
            else:
                line.append(f' \[`{get_node_str(sub.node_id)}`]')

            return ''.join(line)

        subs = self.bot.session.query(Subscription).filter_by(chat_id=chat_id).all()

        included_subs = [x for x in subs if x.exception == False]
        excluded_subs = [x for x in subs if x.exception == True]

        if not included_subs:
            return _('You have no subscriptions. :(\nTry `/sub events`.')

        msg = [_('You *will receive* notifications from\n')]

        for sub in included_subs:
            msg.append(build_subscription_info(sub))

        if excluded_subs:
            msg.append(_('\n*excluding*\n'))

            for sub in excluded_subs:
                msg.append(build_subscription_info(sub))

        return '\n'.join(msg)


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

