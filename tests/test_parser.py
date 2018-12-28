import datetime

from bs4 import BeautifulSoup

from tkgbot.forum import forum
from tkgbot.forum.forum import Breadcrumb

comment_html = """<article class="comment first odd clearfix">
    <header><h3 class="comment__title comment-title"><a href="/comment/225767#comment-225767" class="permalink"
                                                        rel="bookmark">.</a></h3>
        <p class="submitted"><span class="user-picture"> <a href="/user/2610"
                                                            title="Переглянути профіль користувача."><img
                src="https://www.tkg.org.ua/files/styles/75x75/public/pictures/picture-2610-1432375096.jpg?itok=wRa7OBDI"
                alt="Зображення користувача РоСа." title="Зображення користувача РоСа."></a> </span> <a
                href="/user/2610" title="Переглянути профіль користувача." class="username">TestUser</a> replied on
            <time pubdate="" datetime="2018-08-08T16:07:00+03:00">Срд, 08/08/2018 - 16:07</time>
            <a href="/comment/225767#comment-225767" class="permalink" rel="bookmark">#</a></p>
    </header>
    <div class="field field-name-field-vote field-type-vud-field field-label-hidden">
        <div class="field-items">
            <div class="field-item even">
                <div class="vud-widget vud-widget-alternate" id="widget-comment-225767"><a
                        href="/vote/comment/225767/1/vote/alternate/paVcIRacEpVJskxSz-nTRTP54pFqTzoTjC4mwDzLDNM/nojs"
                        rel="nofollow" class="vud-link-up use-ajax ajax-processed">
                    <div class="up-inactive" title="Відмітити"></div>
                    <div class="element-invisible">Відмітити</div>
                </a>
                    <div class="alternate-votes-display">1</div>
                </div>
            </div>
        </div>
    </div>
    <div class="field field-name-comment-body field-type-text-long field-label-hidden">
        <div class="field-items">
            <div class="field-item even"><p></p>
                <p>Test Body.&nbsp;</p></div>
        </div>
    </div>
    <ul class="links inline">
        <li class="comment-reply first"><a href="/comment/reply/35676/225767">відповісти</a></li>
        <li class="quote last"><a href="/comment/reply/35676/225767?quote=1#comment-form"
                                  title="Цитувати цей допис у відповіді.">цитувати</a></li>
    </ul>
</article>"""


def test_parse_simple_comment():
    bs = BeautifulSoup(comment_html, 'html.parser')
    comment_element = bs.findChild()

    comment = forum._parse_comment(comment_element)

    assert comment.link == '/comment/225767#comment-225767'
    assert comment.reply_link == '/comment/reply/35676/225767'
    assert comment.anon == False
    assert comment.subject == None
    assert comment.user_name == 'TestUser'
    assert comment.user_link == "/user/2610"
    assert comment.date == datetime.datetime(2018, 8, 8, 16, 7,
                                             tzinfo=datetime.timezone(datetime.timedelta(seconds=10800)))
    assert comment.is_reply == False



def test_parse_text_body():
    body_html = """
<div class="field-item even">
    <p>Test Body.</p>
</div>
"""
    bs = BeautifulSoup(body_html, 'html.parser')
    body_element = bs.findChild()

    parsed_body = forum._parse_comment_body(body_element)

    result = parsed_body.to_telegram_html()
    assert result == """Test Body."""


def test_parse_body_with_image():
    body_html = """
<div class="field-item even">
    <p>Test Body.</p>
    <img src="https://example.com/test.jpg"></img>
</div>
"""
    bs = BeautifulSoup(body_html, 'html.parser')
    body_element = bs.findChild()

    parsed_body = forum._parse_comment_body(body_element)

    result = parsed_body.to_telegram_html()
    assert result == """Test Body.\n<a href="https://example.com/test.jpg">image</a>"""


def test_parse_body_with_link():
    body_html = """
<div class="field-item even">
    <p>Test Body.</p>
    <p><a href="https://example.com">link</a></p>
</div>
"""
    bs = BeautifulSoup(body_html, 'html.parser')
    body_element = bs.findChild()

    parsed_body = forum._parse_comment_body(body_element)

    result = parsed_body.to_telegram_html()
    assert result == """Test Body.\n<a href="https://example.com">link</a>"""


def test_parse_body_with_br():
    body_html = """
<div class="field-item even">
    <p>Line1<br>Line2</p>
</div>
"""
    bs = BeautifulSoup(body_html, 'html.parser')
    body_element = bs.findChild()

    parsed_body = forum._parse_comment_body(body_element)

    result = parsed_body.to_telegram_html()
    assert result == """Line1\nLine2"""


def test_parse_body_with_nbsp():
    body_html = """
<div class="field-item even">
    <p>&nbsp;Line1&nbsp;Line2&nbsp;</p>
    <p>&nbsp;</p>
</div>
"""
    bs = BeautifulSoup(body_html, 'html.parser')
    body_element = bs.findChild()

    parsed_body = forum._parse_comment_body(body_element)

    result = parsed_body.to_telegram_html()
    assert result == """ Line1 Line2"""


def test_parse_unordered_list():
    body_html = """
<div class="field-item even">
    <ul>
        <li>item1</li>
        <li>item2</li>
    </ul>
</div>
"""
    bs = BeautifulSoup(body_html, 'html.parser')
    body_element = bs.findChild()

    parsed_body = forum._parse_comment_body(body_element)

    result = parsed_body.to_telegram_html()
    assert result == """  ◦ item1\n  ◦ item2"""


def test_parse_table():
    body_html = """
<div class="field-item even">
    <table>
        <tr>
            <td>A</td>
            <td>B</td>
        </tr> 
        <tr>
            <td>C</td>
            <td>D</td>
        </tr> 
    </table>
</div>
"""
    bs = BeautifulSoup(body_html, 'html.parser')
    body_element = bs.findChild()

    parsed_body = forum._parse_comment_body(body_element)

    result = parsed_body.to_telegram_html()
    assert result == """A | B\nC | D"""


def test_parse_email():
    body_html = """
<div>
    <script type="text/javascript">
    <!--//--><![CDATA[// ><!--
    eval(unescape(''%64%6f%63%75%6d%65%6e%74%2e%77%72%69%74%65%28%27%3c%61%20%68%72%65%66%3d%22%6d%61%69%6c%74%6f%3a%6d%61%69%6c%40%67%6d%61%69%6c%2e%63%6f%6d%22%3e%6d%61%69%6c%40%67%6d%61%69%6c%2e%63%6f%6d%3c%2f%61%3e%27%29%3b''))
    //--><!]]>
    </script>
</div>
"""
    bs = BeautifulSoup(body_html, 'html.parser')
    body_element = bs.findChild()

    parsed_body = forum._parse_comment_body(body_element)

    result = parsed_body.to_telegram_html()
    assert result == """<a href="mailto:mail@gmail.com">mail@gmail.com</a>"""


def test_breadcrumb_parser():
    html = """
    <div class="breadcrumb">
    <span class="inline odd first"><a href="/">Головна</a></span> <span class="delimiter">»</span>
    <span class="inline even"><a href="/forum">Форум</a></span> <span class="delimiter">»</span>
    <span class="inline odd">Клуб</span> <span class="delimiter">»</span> <span class="inline even last">
    <a href="https://www.tkg.org.ua/node/32552">Клуб</a></span></div>
    """

    soup = BeautifulSoup(html, 'html.parser')
    crumbs = forum._parse_breadcrumbs(soup)
    assert crumbs == [
        Breadcrumb('Головна', '/', None),
        Breadcrumb('Форум', '/forum', None),
        Breadcrumb('Клуб', None, None),
        Breadcrumb('Клуб', 'https://www.tkg.org.ua/node/32552', 32552),
    ]
