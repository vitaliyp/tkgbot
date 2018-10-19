'''
    Represent dic as object.
    Implementation stolen from https://goodcode.io/articles/python-dict-object/
'''
import asyncio
from unittest.mock import Mock


class objectview(object):
    def __init__(self, d):
        self.__dict__ = d


def get_mock_coro(return_value=None):
    @asyncio.coroutine
    def mock_coro(*args, **kwargs):
        return return_value

    return Mock(wraps=mock_coro)
