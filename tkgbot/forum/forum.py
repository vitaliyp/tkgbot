import re
import datetime

import bs4
from bs4 import BeautifulSoup
import requests

from tkgbot import secret
from tkgbot.forum.components import Comment, CommentImage, CommentLink, CommentText, ParsedBody, CommentLineBreak
from tkgbot.models import NodeType

NODE_LINK = 'https://www.tkg.org.ua/node/'
ROOT_LINK = 'https://www.tkg.org.ua'

session = requests.Session()


def _check_loginned(soup):
    profile_link = soup.find('a', href='/user')
    return bool(profile_link)


def _login():
    data = {
        'pass': secret.forum['password'],
        'name': secret.forum['login'],
        'form_id': 'user_login',
    }
    session.post('https://www.tkg.org.ua/user',
                 data=data, allow_redirects=False)


def visit_topic(link):
    link = ''.join((ROOT_LINK, link))
    session.get(link)


def get_id_from_link(link):
    m = re.match(r'/node/([\d]+)', link)
    if m:
        return int(m.group(1))
    else:
        return None


def _parse_topic(tr):
        topic = {}

        topic_type_str = tr.find(class_='views-field-type').text.strip()
        topic['type'] = {'Тема в форумі': NodeType.TOPIC,
                         'Матеріал': NodeType.MATERIAL,
                         'Подія': NodeType.EVENT,
                         'Новина': NodeType.NEWS}.get(topic_type_str, None)
        if not topic['type']:
            return None

        title_a = tr.find(class_='views-field-title').a
        extracted_mark = title_a.mark.extract()
        topic['name'] = title_a.text.strip()
        if extracted_mark['class'] and extracted_mark['class'][0] in ('updated', 'new'):
            topic['status'] = extracted_mark['class'][0]
        else:
            return None
        topic['link'] = title_a['href']
        node_id = get_id_from_link(topic['link'])
        if not node_id:
            return None
        topic['node_id'] = node_id
        section_a = tr.find('td', class_='views-field-og-group-ref').a
        if section_a:
            topic['section_name'] = section_a.text.strip()
            topic['section_link'] = section_a['href']

            section_node_id = get_id_from_link(topic['section_link'])
            topic['section_node_id'] = section_node_id
        else:
            topic['section_name'] = None
            topic['section_link'] = None
            topic['section_node_id'] = None

        count_el = tr.find('td', class_='views-field-comment-count')
        count_strings = list(count_el.stripped_strings)
        new_count = None
        total_count = None
        try:
            if not count_strings or len(count_strings) > 2:
                return None
            if len(count_strings) == 2:
                new_count = int(count_strings[1].split()[0])
            total_count = int(count_strings[0])
        except ValueError:
            return None
        new_comments_link_a = count_el.find('a')
        topic['new_comments_link'] = new_comments_link_a['href'] if new_comments_link_a else None
        topic['new_messages_count'] = new_count
        topic['messages_count'] = total_count

        return topic


def get_updated_topics():
    topics = []

    resp = session.get('https://www.tkg.org.ua/tracker')
    soup = BeautifulSoup(resp.text, 'html.parser')

    if not _check_loginned(soup):
        _login()

    tbody = soup.find(id='footable').tbody
    marks = tbody.find_all('mark')
    for mark in marks:
        tr = mark.find_parent('tr')
        topic = _parse_topic(tr)
        if topic:
            topics.append(topic)

    return topics


def _get_other_pages_links(soup):
    pager = soup.find('ul', class_='pager')
    if not pager:
        return []

    links = []
    for li in pager.find_all('li', class_='pager-item'):
        links.append(li.a['href'])

    return links


def _parse_datetime(datetime_string):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})([+-]\d{2}):(\d{2})', datetime_string)
    if not m:
        return None

    data = [int(d) for d in m.groups()]

    tz = datetime.timezone(datetime.timedelta(hours=data[6], minutes=data[7]))

    return datetime.datetime(data[0], data[1], data[2], data[3], data[4], data[5], tzinfo=tz)


def _parse_tag(tag: bs4.Tag):
    parts_list = []

    for child in tag.children:
        if isinstance(child, bs4.NavigableString):
            string = str(child.string)
            # replace &nbsp with spaces
            string = string.replace(chr(160), ' ')
            if string and string != '\n':
                parts_list.append(CommentText(string))
        if isinstance(child, bs4.Tag):
            tag_name = child.name
            if tag_name == 'a':
                href = child.get('href')
                text = ' '.join(string for string in child.stripped_strings if string)
                parts_list.append(CommentLink(text=text, href=href))
            elif tag_name == 'p':
                parsed_components = _parse_tag(child)
                if parsed_components:
                    parts_list.extend(parsed_components)
                    parts_list.append(CommentLineBreak())
            elif tag_name == 'br':
                parts_list.append(CommentLineBreak())
            elif tag_name == 'img':
                src = child.get('src')
                parts_list.append(CommentImage(src))
            else:
                parts_list.extend(_parse_tag(child))

    return parts_list


def _parse_comment_body(body: bs4.Tag):
    parts_list = _parse_tag(body)
    strings = body.stripped_strings
    parsed_body = ParsedBody('\n'.join(strings), parts_list)
    return parsed_body


def _parse_comment(comment_el):
    comment = Comment()
    # Check if comment is a reply
    comment['is_reply'] = bool(comment_el.find_parent('div', class_='indented'))
    header = comment_el.header
    subj_a = header.find('a', class_='permalink')
    subject = subj_a.text
    comment['subject'] = subj_a.text if subj_a.text not in ('.', '') else None
    comment['link'] = subj_a['href']
    submitted = header.find('p', class_='submitted')
    username_el = submitted.find(class_='username')
    user_name = username_el.text
    comment['user_name'] = user_name

    anon = username_el.name != 'a'
    comment['anon'] = anon
    if not anon:
        comment['user_link'] = username_el['href']

    datetime_str = submitted.time['datetime']
    datetime = _parse_datetime(datetime_str)
    comment['date'] = datetime
    comment_body_raw = comment_el.find('div', class_='field-name-comment-body').find('div', class_='field-item')
    comment_body = _parse_comment_body(comment_body_raw)
    comment['body'] = comment_body
    reply_link = comment_el.find('li', class_='comment-reply').a['href']
    comment['reply_link'] = reply_link
    quote_link = comment_el.find('li', class_='quote').a['href']
    comment['quote_link'] = quote_link
    return comment


def _get_new_comments_on_page(soup):
    marks = soup.find_all('mark', class_='new')
    comments = []
    for mark in marks:
        comment_el = mark.find_parent('article', class_='comment')
        comment = _parse_comment(comment_el)
        comments.append(comment)

    return comments


def get_new_comments_in_topic(link):
    page = session.get(''.join((ROOT_LINK, link)))
    soup = BeautifulSoup(page.text, 'html.parser')
    comments = _get_new_comments_on_page(soup)
    return comments


_login()

if __name__ == '__main__':
    pass
