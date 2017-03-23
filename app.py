from flask import Flask
from flask import request
from flask import jsonify
import secret
import requests

import subscriptions

app = Flask(__name__)

MSG_INCORRECT_COMMAND='Incorrect command. Use /list for the list of commands.'
MSG_NO_COMMAND='Use /list for the list of commands.'
MSG_LIST='/show - Show your subscriptions\n/sub node - Subscribe\n/unsub node - Unsubscribe\n/unsuball - Remove all subscriptions\n/list - Show this message'
MSG_OK = 'Ok.'

@app.route('/testbot/hooks/%s/'%secret.token, methods=['POST'])
def hello_world():
    rjson = request.get_json();
    print(rjson)
    if 'message' not in rjson:
        return ''

    message = rjson['message']['text']
    chat_id = rjson['message']['chat']['id']

    return_message = ''

    message_list = message.split()
    if message[0].startswith('/'):
        command = message_list[0][1:]
        if command == 'sub':
            try:
                node = int(message_list[1])
                subscriptions.subscribe(chat_id=chat_id, node=node)            
                return_message = MSG_OK
            except (ValueError, IndexError):
                return_message = MSG_INCORRECT_COMMAND
        elif command == 'unsub':
            try:
                node = int(message_list[1])
                subscriptions.unsubscribe(chat_id=chat_id, node=node)            
                return_message = MSG_OK
            except (ValueError, IndexError):
                return_message = MSG_INCORRECT_COMMAND
        elif command == 'unsuball':
            subscriptions.unsubscribe_all(chat_id)
            return_message = MSG_OK
        elif command == 'show':
            subs = subscriptions.get_subscriptions(chat_id)
            return_message = str([sub[2] for sub in subs])
        elif command == 'list':
            return_message = MSG_LIST
        else:
            return_message = ''
    else:
        return_message = MSG_LIST 

    params = {'chat_id': chat_id,
        'text': return_message,
        'method': 'sendMessage',
        'parse_mode':'markdown',
    }

    #r = requests.post('https://api.telegram.org/bot%s/sendMessage'%secret.token, params=params)

    return jsonify(params) 

@app.route('/testbot/test')
def test():
    return 'OK'
