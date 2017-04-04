import re
import datetime

from bs4 import BeautifulSoup
import requests

import secret
from models import NodeType

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
    m = re.match('/node/([\d]+)', link)
    if m:
        return int(m.group(1))
    else:
        return None


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
        topic = {}

        topic_type_str = tr.find(class_='views-field-type').text.strip()
        topic['type'] = {'Тема в форумі': NodeType.TOPIC,
                         'Матеріал': NodeType.MATERIAL,
                         'Подія': NodeType.EVENT,
                         'Новина': NodeType.NEWS}.get(topic_type_str, None)
        if not topic['type']:
            continue

        title_a = tr.find(class_='views-field-title').a
        extracted_mark = title_a.mark.extract()
        topic['name'] = _escape_markdown(title_a.text.strip())
        if extracted_mark['class'] and extracted_mark['class'][0] in ('updated', 'new'):
            topic['status'] = extracted_mark['class'][0]
        else:
            continue
        topic['link'] = title_a['href']
        node_id = get_id_from_link(topic['link'])
        if not node_id:
            continue
        topic['node_id'] = node_id
        section_a = tr.find('td', class_='views-field-og-group-ref').a
        if section_a:
            topic['section_name'] = _escape_markdown(section_a.text.strip())
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
                continue
            if len(count_strings) == 2:
                new_count = int(count_strings[1].split()[0])
            total_count = int(count_strings[0])
        except ValueError:
            continue
        new_comments_link_a = count_el.find('a')
        topic['new_comments_link'] = new_comments_link_a['href'] if new_comments_link_a else None
        topic['new_messages_count'] = new_count
        topic['messages_count'] = total_count

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
    m = re.match('(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})([+-]\d{2}):(\d{2})', datetime_string)
    if not m:
        return None

    data = [int(d) for d in m.groups()]

    tz = datetime.timezone(datetime.timedelta(hours=data[6], minutes=data[7]))

    return datetime.datetime(data[0], data[1], data[2], data[3], data[4], data[5], tzinfo=tz)


def _escape_markdown(text):
    result_text = text
    for c in ['_', '*', '[', ']', '(', ')', '`']:
        result_text = result_text.replace(c, '\\'+c)
    return result_text


def _parse_comment_body(body):
    strings = body.stripped_strings
    escaped_strings = [_escape_markdown(string) for string in strings]
    return '\n'.join(escaped_strings)


def _get_new_comments_on_page(soup):
    marks = soup.find_all('mark', class_='new')
    comments = []
    for mark in marks:
        comment = {}
        comment_el = mark.find_parent('article', class_='comment')

        # Check if comment is a reply
        comment['is_reply'] = bool(comment_el.find_parent('div', class_='indented'))

        header = comment_el.header

        subj_a = header.find('a', class_='permalink')
        subject = subj_a.text
        comment['subject'] = subj_a.text if subj_a.text not in ('.', '')  else None
        comment['link'] = subj_a['href']

        submitted = header.find('p', class_='submitted')
        username_el = submitted.find(class_='username')
        user_name = username_el.text
        comment['user_name'] = _escape_markdown(user_name)
        if username_el.name == 'a':
            comment['anon'] = False
            comment['user_link'] = username_el['href']
        else:
            comment['anon'] = True

        datetime_str = submitted.time['datetime']
        datetime = _parse_datetime(datetime_str)
        comment['date'] = datetime

        comment_body_raw = comment_el.find('div', class_='field-item')
        comment_body = _parse_comment_body(comment_body_raw)
        comment['body'] = comment_body

        reply_link = comment_el.find('li', class_='comment-reply').a['href']
        comment['reply_link'] = reply_link

        quote_link = comment_el.find('li', class_='quote').a['href']
        comment['quote_link'] = quote_link

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
