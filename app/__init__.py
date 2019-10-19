import os

from flask import Flask, jsonify, send_from_directory

from .models import Tweet
from .bot import TrumpBot
from .config import configure_app

app = Flask(__name__)
configure_app(app, status='production')


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/json')
def json():
    return jsonify([tweet.serialize() for tweet in Tweet.objects.all()])


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    web_dir = app.config.get('WEB_DIR')
    if path != "" and os.path.exists('%s/%s' % (web_dir, path)):
        return send_from_directory('%s/%s' % (web_dir, path))
    else:
        return send_from_directory('%s/' % web_dir, 'index.html')
