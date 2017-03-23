import requests
import secret 
from collections import defaultdict 
import forum
import subscriptions
import datetime

def send_message_new_comments(users):
    for user, updates in users.items():
        messagelist = []
        for topic, comments in updates:
            messagelist.extend(('[', topic['name'], '](', forum.ROOT_LINK, topic['link'], ')'))
            if topic['section_name']:
                messagelist.extend((' - ', '[', topic['section_name'], '](', forum.ROOT_LINK,  topic['section_link'], ')')) 
            messagelist.extend(('\n',))

            for comment in comments:
                messagelist.extend((
                        '*',
                        comment['user_name'], ' wrote ', comment['date'].strftime('%d.%m.%y %H:%M'),
                        '*',
                        ' [#](',forum.ROOT_LINK, comment['link'], ') ',
                        '[reply](', forum.ROOT_LINK, comment['reply_link'], ') ',
                        '\n',
                        comment['body'], '\n',
                        '\n',
                ))

            messagelist.append('\n')

        payload = {
                'chat_id': user,
                'text': ''.join(messagelist),
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True,
                }
        r = requests.post('https://api.telegram.org/bot%s/sendMessage'%secret.token, params=payload)

def run():
    # check forum for topics with new comments
    updated_topics = forum.get_updated_topics()
    # for every topic and it's section find subscribed users
    updates = defaultdict(list) 
    for topic in updated_topics:
        if topic['status']=='updated':
            users = set(subscriptions.get_subscribed_users(topic['node_id']))
            users.update(subscriptions.get_subscribed_users(topic['section_node_id']))
            users.update(subscriptions.get_subscribed_users(0))

            comments = forum.get_new_comments_in_topic(topic['link'])

            print(users)
            print(comments)


            for user in users:
                updates[user].append((topic, comments))

    send_message_new_comments(updates)


    # send messages to users

if __name__=='__main__':
    run()
