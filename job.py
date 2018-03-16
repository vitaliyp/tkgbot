from collections import defaultdict

import datetime
import requests

import database
import secret
import forum
from models import Subscription, Node, NodeType
import database
from settings import translation

_ = translation.gettext


def _escape_html_characters(text: str):
    result_text = text
    result_text = result_text.replace('&', '&amp;')
    result_text = result_text.replace('<', '&lt;')
    result_text = result_text.replace('>', '&gt;')
    result_text = result_text.replace('"', '&quot;')

    return result_text


def _format_html_bold(text: str) -> str:
    return '<strong>' + text + '</strong>'


def _format_html_link(link: str, text: str) -> str:
    return '<a href="' + link + '">' + text + '</a>'


def _construct_topic_header(topic):
    l = []
    l.extend((
        _format_html_link(forum.ROOT_LINK + topic['link'], _escape_html_characters(topic['name'])),
    ))
    if topic['section_name']:
        l.extend((
            ' - ',
            _format_html_link(forum.ROOT_LINK + topic['section_link'], _escape_html_characters(topic['section_name'])),
        ))
    l.append('\n')
    return ''.join(l)


def _construct_comment(comment):
    l = []
    l.extend([
        _format_html_bold(_escape_html_characters(comment['user_name'])
                          + ' | '
                          + comment['date'].strftime('%d.%m.%y %H:%M'),
                          ),
        ' ',
        _format_html_link(forum.ROOT_LINK + comment['link'], _('link')),
        ' ',
        _format_html_link(forum.ROOT_LINK + comment['reply_link'], _('reply')),
        '\n',
    ])
    if comment['subject']:
        l.extend((_escape_html_characters(comment['subject'].upper()), '\n'))
    l.extend((_escape_html_characters(comment['body']), '\n'))
    return ''.join(l)


class NewCommentsMessageBuilder:
    def __init__(self, maxsize):
        self._maxsize = maxsize
        self._reset()

    def _reset(self):
        self._list = []
        self._size = 0
        self._has_topics = False
        self._current_topic_has_comments = False
        self._current_topic = None
        self._current_header = None

    def _append(self, msg_part):
        self._list.append(msg_part)
        self._size += len(msg_part)

    def get_message(self):
        if self._size:
            return ''.join(self._list)
        return None

    def add_comment(self, topic, comment):
        if self._current_topic is not topic or not self._current_header:
            self._current_header = _construct_topic_header(topic)
            self._current_topic = topic
            self._current_topic_has_comments = False

        header_str = self._current_header if not self._current_topic_has_comments else ''
        blanks_before_header = '\n\n' if header_str and self._has_topics else ''
        blanks_before_comment = '\n' if self._current_topic_has_comments else ''
        comment_str = _construct_comment(comment)

        msg_part = ''.join([blanks_before_header, header_str, blanks_before_comment, comment_str])

        if self._size + len(msg_part) < self._maxsize:
            self._append(msg_part)
            self._current_topic_has_comments = True
            self._has_topics = True
            return None
        else:
            if len(msg_part) >= self._maxsize:
                msg_part = msg_part[:self._maxsize - 3] + '...'
            msg = self.get_message()
            self._list = []
            self._size = 0
            self._append(msg_part)
            self._current_topic_has_comments = True
            return msg


def send_message(chat_id, text):
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
    }
    r = requests.post('https://api.telegram.org/bot%s/sendMessage' % secret.token, params=payload)


def send_message_new_comments(comment_updates):
    for user, updates in comment_updates.items():
        builder = NewCommentsMessageBuilder(maxsize=4000)
        for topic, comments in updates:
            for comment in comments:
                msg = builder.add_comment(topic, comment)
                if msg:
                    send_message(user, msg)
        msg = builder.get_message()
        if msg:
            send_message(user, msg)


def send_message_new_topics(topic_updates):
    for user, updates in topic_updates.items():
        msg_list = [_('New topics:'), '\n']
        for topic in updates:
            msg_list.append(_construct_topic_header(topic))
            msg_list.append('\n')
        msg = ''.join(msg_list)
        send_message(user, msg)


def run():
    Session = database.get_db_session()
    session = Session()
    database.Base.query = Session.query_property()

    updates_comments_new = defaultdict(list)
    updates_topics_new = defaultdict(list)
    updated_topics = forum.get_updated_topics()
    for topic in updated_topics:
        # Find or create node for this topic
        node = Node.query.filter_by(id=topic['node_id']).first()
        if not node:
            node = Node(id=topic['node_id'], name=topic['name'])
            session.add(node)
        node.name = topic['name']
        # find parent of this node
        parent_node = node.parent
        if not parent_node:
            if topic['section_node_id']:
                parent_node = Node.query.filter_by(id=topic['section_node_id']).first()
                if not parent_node:
                    parent_node = Node(id=topic['section_node_id'],
                                       parent_id=NodeType.TOPIC.value,
                                       name=topic['section_name'])
                parent_node.name = topic['section_name']
            else:
                if topic['type'] in [NodeType.EVENT, NodeType.NEWS, NodeType.MATERIAL]:
                    parent_node = Node.query.filter_by(id=topic['type'].value).one()
                else:
                    raise Exception('Cannot find parent for node')
            node.parent = parent_node
        last_checked = node.last_checked
        node.last_checked = datetime.datetime.now()
        session.commit()

        current_node = node
        excepted = set()
        subscribed = {}
        while current_node:
            subscriptions = current_node.subscriptions
            for s in subscriptions:
                if s.exception:
                    excepted.add(s.chat_id)
                else:
                    if s.chat_id not in excepted and s.chat_id not in subscribed:
                        subscribed[s.chat_id] = s
            current_node = current_node.parent
        print(subscribed)

        if topic['new_comments_link']:
            comments = forum.get_new_comments_in_topic(topic['new_comments_link'])
        else:
            comments = []

        for chat_id, subscription in subscribed.items():
            if topic['status'] == 'new' and not last_checked:
                updates_topics_new[chat_id].append(topic)
            if comments and not subscription.no_comments:
                if subscription.no_replies:
                    sub_comments = [comment for comment in comments if not comment['is_reply']]
                else:
                    sub_comments = comments
                if sub_comments:
                    updates_comments_new[chat_id].append((topic, sub_comments))

    Session.remove()

    send_message_new_topics(updates_topics_new)
    send_message_new_comments(updates_comments_new)


if __name__ == '__main__':
    run()
