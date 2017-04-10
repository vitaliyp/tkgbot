import unittest
from bs4 import BeautifulSoup

import forum


class TestSesstion(unittest.TestCase):
    def test_check_login(self):
        with open('tests/data/tracker_logged_in.html', 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        self.assertTrue(forum._check_loginned(soup))

        with open('tests/data/tracker_logged_out.html', 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        self.assertFalse(forum._check_loginned(soup))
