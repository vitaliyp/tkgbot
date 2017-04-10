import unittest
from job import NewCommentsMessageBuilder
import datetime

class TestCommentsMessageBuilder(unittest.TestCase):

    def test_simple_comment(self):
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
        expected_msg = ('[Topic_name](https://www.tkg.org.ua/node/123) - '
                    '[Section_name](https://www.tkg.org.ua/node/345)\n'
                    '*username | 02.03.17 01:23* [посилання](https://www.tkg.org.ua/comment_link) '
                    '[відповісти](https://www.tkg.org.ua/reply_link)\n'
                    'SUBJECT\n'
                    'Comment body\n'
                        )

        self.assertEquals(msg, expected_msg)
