import sys
import re

from models import Subscription, Node, NodeType
from database import db_session


MSG_INCORRECT_COMMAND='Incorrect command. Use /help for the list of commands.'
MSG_OK = 'Ok.'


_commands = {}


def command(command_name):
    def wrap(f):
        _commands[command_name] = f
        def wrapped_f(chat_id, args=None):
            if not args:
                args = []
            return f(chat_id, args)
        wrapped_f.__name__ = f.__name__
        return wrapped_f
    command.commands = _commands
    return wrap


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
    choices = {'all': NodeType.ALL,
            'topics': NodeType.TOPIC,
            'materials': NodeType.MATERIAL,
            'events': NodeType.EVENT,
            'news': NodeType.NEWS
            }
    t = choices.get(string, None)
    return t.value if t else None 


@command('sub')
def _command_sub(chat_id, args):
    ''' Subscribe
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
        `/sub 33101 no-replies`'''
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

    node = db_session.query(Node).filter_by(id=node_id).first()
    if not node:
        node = Node(id=node_id)
    subscription = db_session.query(Subscription).filter_by(node_id=node_id, chat_id=chat_id).first()
    if not subscription:
        subscription = Subscription(node=node, chat_id=chat_id)
    subscription.exception = exception
    subscription.no_comments = no_comments
    subscription.no_replies = no_replies

    db_session.add(subscription)
    db_session.commit()

    return MSG_OK


@command('help')
def _command_help(chat_id, args):
    '''Show this help message.'''
    str_list = []
    for c_name, c in command.commands.items():
        str_list.extend(('/', c_name))
        if c.__doc__:
            lines = c.__doc__.expandtabs().splitlines()
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
    return  ''.join(str_list) 


@command('unsub')
def _command_unsub(chat_id, args):
    '''Unsubscribe'''
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

    db_session.query(Subscription).filter_by(node_id=node_id, chat_id=chat_id).delete()
    db_session.commit()

    return MSG_OK


@command('unsuball')
def _command_unsuball(chat_id, args):
    '''Remove all subscriptions'''
    db_session.query(Subscription).filter_by(chat_id=chat_id).delete()
    db_session.commit()
    return MSG_OK


@command('show')
def _command_show(chat_id, args):
    '''Show your subscriptions'''
    subs = db_session.query(Subscription).filter_by(chat_id=chat_id).all()
    if not subs:
        return 'You have no subscriptions'
    msg_list = []
    node_strs = {NodeType.ALL: 'all',
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


def _command_default(chat_id, args):
    return MSG_INCORRECT_COMMAND


def process_bot_request(data):
    if 'message' not in data:
        return ''
    if 'text' not in data['message']:
        return ''

    message = data['message']['text']
    chat_id = data['message']['chat']['id']

    message_list = message.split()
    if message[0].startswith('/'):
        command = message_list[0][1:]
        args = message_list[1:]
        return_message = _commands.get(command, _command_default)(chat_id, args)
    else:
        return_message = _command_help(chat_id, []) 

    params = {'chat_id': chat_id,
        'text': return_message,
        'method': 'sendMessage',
        'parse_mode':'markdown',
    }

    return params

