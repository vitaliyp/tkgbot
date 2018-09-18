import datetime
import enum
from dataclasses import dataclass, field
from typing import List


@dataclass
class Comment:
    link: str = None
    is_reply: bool = None
    reply_link: str = None
    date: datetime.datetime = None
    anon: bool = None
    user_name: str = None
    user_link: str = None
    subject: str = None
    body: 'ParsedBody' = None

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value


class BodyComponent:
    def to_telegram_html(self):
        raise NotImplementedError


class CommentImage(BodyComponent):
    def __init__(self, src):
        self.src = src

    def to_telegram_html(self):
        return f'<a href="{self.src}">image</a>'


class CommentLink(BodyComponent):
    def __init__(self, text, href):
        self.text = text
        self.href = href

    def to_telegram_html(self):
        return f'<a href="{self.href}">{self.text}</a>'


class CommentText(BodyComponent):
    def __init__(self, text):
        self.text = text

    def to_telegram_html(self):
        return self.text


class CommentLineBreak(BodyComponent):
    def to_telegram_html(self):
        return f'\n'


@dataclass
class ParsedBody:
    body: str
    components: List[BodyComponent] = field(default_factory=lambda: list())

    def __str__(self):
        return self.to_telegram_html()

    def to_telegram_html(self):
        return ' '.join(component.to_telegram_html() for component in self. components).strip()