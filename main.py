import os

from dotenv import load_dotenv
load_dotenv(verbose=True)

from app import app
from app.bot import TrumpBotScheduler
from app.models import Tweet


def _initialize_trump_bot() -> TrumpBotScheduler:
    requests_path = os.environ.get('REQUESTS_FILE_PATH', 'requests/request.json')
    auth_path = os.environ.get('AUTH_FILE_PATH', 'requests/auth.json')
    trump_bot = TrumpBotScheduler(file_path=requests_path, auth_file_path=auth_path)

    # this functions initialize the trump bot by getting the latest tweets
    # and trying to send any tweets that contained errors
    trump_bot.send_latest_tweets()
    trump_bot.resend_bad_tweets()
    return trump_bot


def _start_flask_server():
    port = app.config.get('PORT')
    app.run(host='0.0.0.0', port=port)


if __name__ == "__main__":
    bot = _initialize_trump_bot()
    bot.start()

    _start_flask_server()
