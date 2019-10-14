import os

from dotenv import load_dotenv
load_dotenv(verbose=True)

from app import app
from app.bot import TrumpBotScheduler
from app.models import Tweet

if __name__ == "__main__":

    trump_bot = TrumpBotScheduler(file_path='requests/request.json',
                                  auth_file_path='requests/auth.json')
    # # trump_bot.start(seconds=15)
    trump_bot.send_latest_tweets()
    trump_bot.start()

    port = app.config.get('PORT')
    app.run(host='0.0.0.0', port=port)
