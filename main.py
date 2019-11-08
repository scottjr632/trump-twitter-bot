import os
import logging
import argparse
import sys
import signal
import subprocess
from functools import wraps

from dotenv import load_dotenv
load_dotenv(verbose=True)

from app.config import configure_app
from app.bot import TrumpBotScheduler
from app.sentimentbot import SentimentBot

parser = argparse.ArgumentParser(description=r"""
""")


ROOT = os.getcwd()
PID_FILE_PATH = os.path.join(ROOT, 'var/run-dev.pid')
CMDS = []
FNCS = []

try:
    os.setpgrp()

    if not os.path.exists(os.path.dirname(PID_FILE_PATH)):
        os.makedirs(os.path.dirname(PID_FILE_PATH))

    with open(PID_FILE_PATH, 'w+') as file:
        file.write(str(os.getpgrp()) + '\n')

except Exception as e:
    logging.error(e)


def _file_path_sanity_check(*args):
    for path in args:
        if not os.path.exists(path):
            raise Exception('Unable to find file %s' % path)


def _start_client_server(*args, **kwargs):
    cmd = [
        'npm', '--prefix', '%s/client' % ROOT, 'run', 'start'
    ]

    CMDS.append(cmd)


def inject_file_paths(fn):
    requests_path = os.environ.get('REQUESTS_FILE_PATH', 'requests/request.json')
    auth_path = os.environ.get('AUTH_FILE_PATH', 'requests/auth.json')
    _file_path_sanity_check(requests_path, auth_path)

    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(requests_path=requests_path, auth_path=auth_path, *args, **kwargs)

    return wrapper


@inject_file_paths
def _initialize_trump_bot(auth_path, requests_path, 
                          send_posts: bool=True,
                          *args, **kwargs) -> TrumpBotScheduler:

    trump_bot: TrumpBotScheduler = None
    if send_posts:
        logging.info('Post requests are not being sent.')

        class PostOverride(TrumpBotScheduler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def __send_tweet_msg__(self, content, headers=None):
                return 200
        
        trump_bot = PostOverride(file_path=requests_path, auth_file_path=auth_path)

    else:
        trump_bot = TrumpBotScheduler(file_path=requests_path, auth_file_path=auth_path)


    # this functions initialize the trump bot by getting the latest tweets
    # and trying to send any tweets that contained errors
    trump_bot.send_latest_tweets()
    trump_bot.resend_bad_tweets()
    logging.info('Trump bot initialization finished... please press ctrl-c to close program if finished.')
    return trump_bot


@inject_file_paths
def _start_sentiment_bot(auth_path: str, requests_path: str, 
                         trump_bot: TrumpBotScheduler, 
                         send_posts: bool=True) -> SentimentBot:

    bot: SentimentBot = None
    if send_posts:
        logging.info('Sentiment bot is not running')

        class PostOverride(SentimentBot):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def __send_tweet_msg__(self, content) -> int:
                return 200

        bot = PostOverride(file_path=requests_path, auth_file_path=auth_path)
    
    else:
        bot = SentimentBot(auth_file_path=auth_path, file_path=requests_path)

    trump_bot.add_job(bot.send_todays_tone, 'interval', hours=24, max_instances=1)
    return bot


def _start_flask_server(*args, **kwargs):
    from app import app

    logging.info('Starting the flask server...')
    level = os.environ.get('CONFIG_LEVEL')

    configure_app(app, status='production' if level is None else level)
    port = app.config.get('PORT')
    app.run(host='0.0.0.0', port=port)  


def _start_dev_server(*args, **kwargs):
    _start_client_server()

    FNCS.append(_start_flask_server)


def _start_prod_server(*args, **kwargs):
    _start_trump_bot(*args, **kwargs)
    _start_flask_server(*args, **kwargs)


def _start_trump_bot(send_posts=True, start_sentiment_bot=False, *args, **kwargs):
    logging.info('Starting the trump bot...')
    # requests_path = os.environ.get('REQUESTS_FILE_PATH', 'requests/request.json')
    # auth_path = os.environ.get('AUTH_FILE_PATH', 'requests/auth.json')
    # _file_path_sanity_check(requests_path, auth_path)

    bot = _initialize_trump_bot(send_posts=send_posts)
    if not start_sentiment_bot: 
        _start_sentiment_bot(trump_bot=bot, send_posts=send_posts)

    bot.start()


ACTIONS = {
    "initialize": _initialize_trump_bot,
    "client": _start_client_server,
    "trumpbot": _start_trump_bot,
    "flask": _start_flask_server,
    "dev": _start_dev_server,
    "prod": _start_prod_server,
}


parser.add_argument('action',
                    help='start the Flask app',
                    type=str,
                    choices=[key for key, v in ACTIONS.items()])

parser.add_argument('-np', '--no-post',
                    dest='send_posts',
                    action='store_true',
                    help='Do not send post requests')

parser.add_argument('-nsb', '--no-sentiment-bot',
                    dest='start_sentiment_bot',
                    action='store_true',
                    help='Do not to start the sentiment bot')


def signal_handler(sig, frame):
    os.killpg(0, signal.SIGTERM)
    os.remove(PID_FILE_PATH)
    sys.exit(0)


def main():
    options = parser.parse_args()
    for s in (signal.SIGINT, signal.SIGTERM):
        signal.signal(s, signal_handler)
    
    ACTIONS.get(options.action)(**options.__dict__)
    env = os.environ.copy()
    for cmd in CMDS:
        subprocess.Popen(cmd, env=env)

    for fn in FNCS:
        subprocess.Popen(fn(), env=env)

    signal.pause()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
