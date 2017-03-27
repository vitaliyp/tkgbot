from flask import Flask
from flask import request, jsonify
from database import Session

import secret
import tkgbot

application = Flask(__name__)


@application.route('/testbot/hooks/%s/'%secret.token, methods=['POST'])
def bot():
    data = request.get_json()
    response_data = tkgbot.process_bot_request(data)
    return jsonify(response_data) 
