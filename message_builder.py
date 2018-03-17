from settings import translation

import forum

_ = translation.gettext

class NewCommentsMessageBuilder:
    def __init__(self, maxsize):
        self._maxsize = maxsize
        self._reset()

    @classmethod
    def _escape_html_characters(cls, text: str):
        result_text = text
        result_text = result_text.replace('&', '&amp;')
        result_text = result_text.replace('<', '&lt;')
        result_text = result_text.replace('>', '&gt;')
        result_text = result_text.replace('"', '&quot;')

        return result_text

    @classmethod
    def _format_html_bold(cls, text: str) -> str:
        return '<strong>' + text + '</strong>'

    @classmethod
    def _format_html_link(cls, link: str, text: str) -> str:
        return '<a href="' + link + '">' + text + '</a>'

    @classmethod
    def _construct_topic_header(cls, topic):
        l = []
        l.extend((
            cls._format_html_link(forum.ROOT_LINK + topic['link'], cls._escape_html_characters(topic['name'])),
        ))
        if topic['section_name']:
            l.extend((
                ' - ',
                cls._format_html_link(forum.ROOT_LINK + topic['section_link'], cls._escape_html_characters(topic['section_name'])),
            ))
        l.append('\n')
        return ''.join(l)

    @classmethod
    def _construct_comment(cls, comment):
        l = []
        l.extend([
            cls._format_html_bold(cls._escape_html_characters(comment['user_name'])
                              + ' | '
                              + comment['date'].strftime('%d.%m.%y %H:%M'),
                              ),
            ' ',
            cls._format_html_link(forum.ROOT_LINK + comment['link'], _('link')),
            ' ',
            cls._format_html_link(forum.ROOT_LINK + comment['reply_link'], _('reply')),
            '\n',
        ])
        if comment['subject']:
            l.extend((cls._escape_html_characters(comment['subject'].upper()), '\n'))
        l.extend((cls._escape_html_characters(comment['body']), '\n'))
        return ''.join(l)

    def _reset(self):
        self._list = []
        self._size = 0
        self._has_topics = False
        self._current_topic_has_comments = False
        self._current_topic = None
        self._current_header = None

    def _append(self, msg_part):
        self._list.append(msg_part)
        self._size += len(msg_part)

    def get_message(self):
        if self._size:
            return ''.join(self._list)
        return None

    def add_comment(self, topic, comment):
        if self._current_topic is not topic or not self._current_header:
            self._current_header = self._construct_topic_header(topic)
            self._current_topic = topic
            self._current_topic_has_comments = False

        header_str = self._current_header if not self._current_topic_has_comments else ''
        blanks_before_header = '\n\n' if header_str and self._has_topics else ''
        blanks_before_comment = '\n' if self._current_topic_has_comments else ''
        comment_str = self._construct_comment(comment)

        msg_part = ''.join([blanks_before_header, header_str, blanks_before_comment, comment_str])

        if self._size + len(msg_part) < self._maxsize:
            self._append(msg_part)
            self._current_topic_has_comments = True
            self._has_topics = True
            return None
        else:
            if len(msg_part) >= self._maxsize:
                msg_part = msg_part[:self._maxsize - 3] + '...'
            msg = self.get_message()
            self._list = []
            self._size = 0
            self._append(msg_part)
            self._current_topic_has_comments = True
            return msg