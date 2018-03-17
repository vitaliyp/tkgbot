import unittest
from message_builder import NewCommentsMessageBuilder
import job
import datetime


class TestCommentsMessageBuilder(unittest.TestCase):
    def test_simple_comment(self):
        self.maxDiff = None

        builder = NewCommentsMessageBuilder(maxsize=1000)
        comment = {
            'body': 'Comment body',
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

        result = builder.add_comment(topic, comment)
        self.assertIsNone(result)
        msg = builder.get_message()
        expected_msg = ('<a href="https://www.tkg.org.ua/node/123">Topic_name</a> - '
                        '<a href="https://www.tkg.org.ua/node/345">Section_name</a>\n'
                        '<strong>username | 02.03.17 01:23</strong> '
                        '<a href="https://www.tkg.org.ua/comment_link">посилання</a> '
                        '<a href="https://www.tkg.org.ua/reply_link">відповісти</a>\n'
                        'SUBJECT\n'
                        'Comment body\n'
                        )

        self.assertEquals(msg, expected_msg)


class TestEscaping(unittest.TestCase):
    def test_html_escaping(self):
        self.assertEquals(NewCommentsMessageBuilder._escape_html_characters(''), '')
        self.assertEquals(NewCommentsMessageBuilder._escape_html_characters('<'), '&lt;')
        self.assertEquals(NewCommentsMessageBuilder._escape_html_characters('>'), '&gt;')
        self.assertEquals(NewCommentsMessageBuilder._escape_html_characters('&'), '&amp;')
        self.assertEquals(NewCommentsMessageBuilder._escape_html_characters('"'), '&quot;')
        self.assertEquals(NewCommentsMessageBuilder._escape_html_characters('asd&as<strong>asd'),
                          'asd&amp;as&lt;strong&gt;asd')


class TestFormatting(unittest.TestCase):
    def test_format_html_bold(self):
        self.assertEquals(NewCommentsMessageBuilder._format_html_bold('test'), '<strong>test</strong>')

    def test_format_html_link(self):
        self.assertEquals(NewCommentsMessageBuilder._format_html_link('link', 'text'),
                          '<a href="link">text</a>')
