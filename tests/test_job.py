import unittest

from tkgbot.forum.components import Comment, ParsedBody, CommentText, TopicHeader
from tkgbot import message_builder
import datetime
from tkgbot.utils import escape_html_characters

comment_data = {
    'body': ParsedBody('Comment body', [CommentText('Comment body')]),
    'user_name': 'username',
    'date': datetime.datetime(year=2017, month=3, day=2, hour=1, minute=23, second=34),
    'subject': 'Subject',
    'link': '/comment_link',
    'reply_link': '/reply_link',
}

topic = {
    'name': 'Topic_name',
    'section_name': 'Section_name',
    'link': '/node/123',
    'section_link': '/node/345',
}

new_topic_message = TopicHeader(
    body=comment_data['body'],
    user_name=comment_data['user_name'],
    date=comment_data['date'],
)

new_topic = {
    **topic,
    'header_message': new_topic_message,
}


def test_new_topic():
    msg = message_builder.construct_new_topic_message(new_topic)
    expected_msg = ('<strong>New topic:</strong>\n'
                    '<a href="https://www.tkg.org.ua/node/123">Topic_name</a> - '
                    '<a href="https://www.tkg.org.ua/node/345">Section_name</a>\n'
                    '<strong>username | 02.03.17 01:23</strong>\n'
                    'Comment body'
                    )

    assert msg == expected_msg


def test_new_comment():
    comment = Comment(**comment_data)
    msg = message_builder.construct_new_comment_message(topic, comment)
    expected_msg = ('<a href="https://www.tkg.org.ua/node/123">Topic_name</a> - '
                    '<a href="https://www.tkg.org.ua/node/345">Section_name</a>\n'
                    '<strong>username | 02.03.17 01:23</strong> '
                    '<a href="https://www.tkg.org.ua/comment_link">посилання</a> '
                    '<a href="https://www.tkg.org.ua/reply_link">відповісти</a>\n'
                    'SUBJECT\n'
                    'Comment body'
                    )

    assert msg == expected_msg


class TestEscaping(unittest.TestCase):
    def test_html_escaping(self):
        self.assertEqual(escape_html_characters(''), '')
        self.assertEqual(escape_html_characters('<'), '&lt;')
        self.assertEqual(escape_html_characters('>'), '&gt;')
        self.assertEqual(escape_html_characters('&'), '&amp;')
        self.assertEqual(escape_html_characters('"'), '&quot;')
        self.assertEqual(escape_html_characters('asd&as<strong>asd'),
                          'asd&amp;as&lt;strong&gt;asd')


class TestFormatting(unittest.TestCase):
    def test_format_html_bold(self):
        self.assertEqual(message_builder._format_html_bold('test'), '<strong>test</strong>')

    def test_format_html_link(self):
        self.assertEqual(message_builder._format_html_link('link', 'text'),
                          '<a href="link">text</a>')
