from collections import defaultdict

import datetime
import requests

from .forum import forum
from .message_builder import NewCommentsMessageBuilder
from .settings import translation, telegram_api_url
from .database import session_scope
from .models import Node, NodeType

_ = translation.gettext


def send_message(chat_id, text):
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
    }
    r = requests.post(telegram_api_url + 'sendMessage', params=payload)


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
            msg_list.append(NewCommentsMessageBuilder._construct_topic_header(topic))
            msg_list.append('\n')
        msg = ''.join(msg_list)
        send_message(user, msg)


def _get_subscriptions(node):
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
    return subscribed


def _get_or_create_topic_node(session, topic):
    node = session.query(Node).filter_by(id=topic['node_id']).first()
    if not node:
        node = Node(id=topic['node_id'], name=topic['name'])
        session.add(node)
    return node


def _get_or_create_parent_node(node, session, topic):
    parent_node = node.parent
    if not parent_node:
        if topic['section_node_id']:
            parent_node = session.query(Node).filter_by(id=topic['section_node_id']).first()
            if not parent_node:
                parent_node = Node(id=topic['section_node_id'],
                                   parent_id=NodeType.TOPIC.value,
                                   name=topic['section_name'])
            parent_node.name = topic['section_name']
            parent_node.parent_id = NodeType.TOPIC.value
        else:
            parent_node = session.query(Node).filter_by(id=topic['type'].value).first()
            if not parent_node:
                raise Exception('Cannot find parent for node')

    return parent_node


def run():
    with session_scope() as session:
        updates_comments_new = defaultdict(list)
        updates_topics_new = defaultdict(list)
        updated_topics = forum.get_updated_topics()
        for topic in updated_topics:
            # Find or create node for this topic
            node = _get_or_create_topic_node(session, topic)

            node.name = topic['name']

            # find parent of this node
            node.parent = _get_or_create_parent_node(node, session, topic)

            last_checked = node.last_checked
            node.last_checked = datetime.datetime.now()
            session.commit()

            subscribed = _get_subscriptions(node)
            print(subscribed)

            if topic['new_comments_link']:
                comments = forum.get_new_comments_in_topic(topic['new_comments_link'])
            else:
                comments = []

            for chat_id, subscription in subscribed.items():
                if topic['status'] == 'new' and not last_checked:
                    updates_topics_new[chat_id].append(topic)

                if not comments or subscription.no_comments:
                    continue

                if subscription.no_replies:
                    sub_comments = [comment for comment in comments if not comment['is_reply']]
                else:
                    sub_comments = comments
                if sub_comments:
                    updates_comments_new[chat_id].append((topic, sub_comments))

        send_message_new_topics(updates_topics_new)
        send_message_new_comments(updates_comments_new)


if __name__ == '__main__':
    run()
