from flask import Flask
from flask import request, jsonify

from database import db_session
import tkgbot
import settings


application = Flask(__name__)


@application.route(settings.webhook_url, methods=['POST'])
def bot():
    data = request.get_json()
    response_data = tkgbot.process_bot_request(data)
    return jsonify(response_data) 

@application.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
