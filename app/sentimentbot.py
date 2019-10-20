import json
import requests

from .sentiment import SentimentWithHistory
from .bot import TrumpBotWithAuth


class SentimentBot(TrumpBotWithAuth, SentimentWithHistory):
    def __init__(self, auth_file_path='auth.json', *args, **kwargs):
        super().__init__(auth_file_path=auth_file_path, *args, **kwargs)

    def __send_tweet_msg__(self, content, headers=None) -> int:
        msg = self._request_body.replace('{{ content }}', self.__clean_content__(content))
        msg_body = json.loads(msg)
        request_url = msg_body['url']
        msg_body['displayname'] = 'Donald J. Trump (Sentiment Bot)'
        if request_url is None:
            raise Exception("Request URL cannot be none type")

        req = requests.post(request_url, json=msg_body, headers=headers)
        return req.status_code

    def send_todays_tone(self):
        todays_tone = self.get_todays_tone_value()
        content = 'Donald J. Trump\'s overall tone for today was %s' % todays_tone
        return self.rebounce_on_401(self.__send_tweet_msg__, content)
