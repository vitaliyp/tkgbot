from .settings import translation
from tkgbot.forum import forum
from tkgbot import utils

_ = translation.gettext


def _format_html_bold(text: str) -> str:
    return '<strong>' + text + '</strong>'


def _format_html_link(link: str, text: str) -> str:
    return '<a href="' + link + '">' + text + '</a>'


def _construct_topic_header(topic):
    l = []
    l.extend((
        _format_html_link(forum.ROOT_LINK + topic['link'], utils.escape_html_characters(topic['name'])),
    ))
    if topic['section_name']:
        l.extend((
            ' - ',
            _format_html_link(forum.ROOT_LINK + topic['section_link'], utils.escape_html_characters(topic['section_name'])),
        ))
    return ''.join(l)


def _construct_comment_body(comment):
    l = []
    l.extend([
        _format_html_bold(utils.escape_html_characters(comment['user_name'])
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
        l.extend((utils.escape_html_characters(comment['subject'].upper()), '\n'))
    l.extend((comment.body.to_telegram_html()))
    return ''.join(l)


def _construct_topic_message_body(comment):
    l = []
    l.extend([
        _format_html_bold(utils.escape_html_characters(comment['user_name'])
                          + ' | '
                          + comment['date'].strftime('%d.%m.%y %H:%M'),
                          ),
        '\n',
    ])
    l.extend((comment.body.to_telegram_html()))
    return ''.join(l)


def construct_new_topic_message(topic):
    parts = [
        _format_html_bold('New topic:'),
        _construct_topic_header(topic),
    ]
    if 'header_message' in topic:
        parts.append(_construct_topic_message_body(topic['header_message']))

    return '\n'.join(parts)


def construct_new_comment_message(topic, comment):
    return '\n'.join((
        _construct_topic_header(topic),
        _construct_comment_body(comment),
    ))
