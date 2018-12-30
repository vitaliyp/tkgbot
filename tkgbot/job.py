from collections import defaultdict

import datetime
import logging
import requests

from tkgbot.telegram.message_dispatch import TelegramMessage, MessagePriority
from .forum import forum
from . import message_builder
from .settings import translation, telegram_api_url
from .database import session_scope
from .models import Node, NodeType

_ = translation.gettext


logger = logging.getLogger(__name__)


def send_message_new_comments(comment_updates, application):
    for user, updates in comment_updates.items():
        for topic, comments in updates:
            for comment in comments:
                msg = message_builder.construct_new_comment_message(topic, comment)
                if msg:
                    message = TelegramMessage(user, msg)
                    application['message_queue'].put_nowait(message, MessagePriority.NOTIFICATION)


def send_message_new_topics(topic_updates, application):
    for user, updates in topic_updates.items():
        for topic in updates:
            msg = message_builder.construct_new_topic_message(topic)
            message = TelegramMessage(user, msg)
            application['message_queue'].put_nowait(message, MessagePriority.NOTIFICATION)


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


def run(application):
    with session_scope() as session:
        updates_comments_new = defaultdict(list)
        updates_topics_new = defaultdict(list)
        try:
            updated_topics = forum.get_updated_topics()
        except requests.ConnectionError as e:
            logger.error(f'Error while making request to the forum: {e}')
            return

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

            topic_created = topic['status'] == 'new' and not last_checked

            if topic_created and topic['type'] == NodeType.TOPIC:
                topic['header_message'] = forum.get_topic_header_message(topic['link'])

            for chat_id, subscription in subscribed.items():
                if topic_created:
                    updates_topics_new[chat_id].append(topic)

                if not comments or subscription.no_comments:
                    continue

                if subscription.no_replies:
                    sub_comments = [comment for comment in comments if not comment['is_reply']]
                else:
                    sub_comments = comments
                if sub_comments:
                    updates_comments_new[chat_id].append((topic, sub_comments))

        send_message_new_topics(updates_topics_new, application)
        send_message_new_comments(updates_comments_new, application)
