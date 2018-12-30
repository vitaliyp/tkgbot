import asyncio

from bs4 import BeautifulSoup

from tkgbot.message_builder import construct_new_comment_message
from tkgbot.forum import forum
from tkgbot.telegram import message_dispatch
from tkgbot.telegram.message_dispatch import TelegramPhotoMessage

raw_comment = """<article class="comment first odd clearfix">
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
                <p>Test Body.&nbsp;</p>
                <p></p>
                <p><a href="https://example.com">Example Link</a> Text after link</p>
                <p><img src="https://example.com/img.jpg"></p>
            </div>
        </div>
    </div>
    <ul class="links inline">
        <li class="comment-reply first"><a href="/comment/reply/35676/225767">відповісти</a></li>
        <li class="quote last"><a href="/comment/reply/35676/225767?quote=1#comment-form"
                                  title="Цитувати цей допис у відповіді.">цитувати</a></li>
    </ul>
</article>"""


async def main():
    parsed_comment = forum._parse_comment(BeautifulSoup(raw_comment, 'html.parser'))
    topic = {
        'name': 'Topic_name',
        'section_name': 'Section_name',
        'link': '/node/123',
        'section_link': '/node/345',

    }

    message = construct_new_comment_message(topic, parsed_comment)

    message = message_dispatch.TelegramMessage(229275810, message)
    sender = message_dispatch.TelegramSender()
    await sender.send_message(message)


async def send_photos():
    photo_link = 'https://www.google.com.ua/images/branding/googlelogo/2x/googlelogo_color_120x44dp.png'
    message = TelegramPhotoMessage(229275810, text='', photo_url=photo_link)
    sender = message_dispatch.TelegramSender()
    await sender.send_message(message)


if __name__ == '__main__':
    asyncio.run(main())
    asyncio.run(send_photos())
