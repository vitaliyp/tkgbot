import unittest

import pytest
from bs4 import BeautifulSoup

from tkgbot.forum import forum


class TestSesstion(unittest.TestCase):
    def test_check_login(self):
        with open('tests/data/tracker_logged_in.html', 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        self.assertTrue(forum._check_loginned(soup))

        with open('tests/data/tracker_logged_out.html', 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        self.assertFalse(forum._check_loginned(soup))


@pytest.mark.parametrize('url,normalized_url', [
    ('node/1234', 'https://www.tkg.org.ua/node/1234'),
    ('/node/1234', 'https://www.tkg.org.ua/node/1234'),
    ('https://www.tkg.org.ua/node/1234', 'https://www.tkg.org.ua/node/1234'),
])
def test_normalize_url(url, normalized_url):
    assert forum.normalize_forum_url(url) == normalized_url
