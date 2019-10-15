import os
import json
import logging
import re
from typing import List

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup

from .models import Tweet
from .auth import Authentication


JSON_MATCHER = r'{.*}'
SYN_TWTR_URL = 'https://cdn.syndication.twimg.com/timeline/profile?callback=__twttr.callbacks.tl_i0_profile_realDonaldTrump_new&dnt=false&lang=en&min_position={}&screen_name=realDonaldTrump&suppress_response_codes=true&t=1745387&tz=GMT-0500&with_replies=false'


def _read_requests_file(file_path) -> str:
    with open(file_path, 'r') as file:
        return file.read()


class TweetExtractor(object):
    def __init__(self, url: str, min_position='', *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.url = url
        self.min_position = min_position

    def _retrieve_latest_tweets_resp(self, min_position: str) -> dict:
        print('getting tweets URL: %s' % self.url.format(self.min_position))
        resp = requests.get(self.url.format(self.min_position))
        if resp.status_code != 200:
            return self.__handle_execption__(resp)
        
        j_body = re.search(JSON_MATCHER, resp.text, re.MULTILINE)
        return json.loads(j_body.group())

    def __handle_execption__(self, resp: requests.Response, ex: Exception=''):
        logging.error(str(ex))

    def _set_min_position(self, min_position: str):
        self.min_position = str(min_position)

    def _set_min_position_from_unparsed_tweets(self, unparsed_tweets: dict):
        headers = unparsed_tweets['headers']
        if headers is None:
            return self.__handle_execption__(None, Exception('Headers was not present in response'))

        new_min_position = headers['maxPosition']
        if new_min_position is None:
            return self.__handle_execption__(None, Exception('Max position was not present'))

        self._set_min_position(new_min_position)

    def get_tweets(self) -> List[Tweet]:
        print('getting tweets')
        unparsed_tweets = self._retrieve_latest_tweets_resp(self.min_position)
        self._set_min_position_from_unparsed_tweets(unparsed_tweets)

        parsed_html = BeautifulSoup(unparsed_tweets['body'])
        tweets = parsed_html.find_all('p', attrs={'class':'timeline-Tweet-text'})
        ids = parsed_html.find_all('div', attrs={'class': 'timeline-Tweet'})

        return [
            Tweet(content=tweet.text, tweet_id=i['data-tweet-id']) 
            for i, tweet in dict(zip(ids, tweets)).items()
        ]


class TrumpBotMessenger(TweetExtractor):
    def __init__(self, file_path='requests.json', *args, **kwargs):
        super().__init__(url=SYN_TWTR_URL, *args, **kwargs)

        self._file_path = file_path
        self._request_body = _read_requests_file(file_path)
        
    def __send_tweet_msg__(self, content: str, headers=None) -> int:
        print('sending message\nContent: %s\nHeaders: %s' % (content, headers))
        msg = self._request_body.replace('{{ content }}', content.replace('\n', ' '))
        msg_body = json.loads(msg)
        request_url = msg_body['url']
        if request_url is None:
            raise Exception("Request URL cannot be none type")

        req = requests.post(request_url, json=msg_body, headers=headers)
        return req.status_code

    def send_latest_tweets(self) -> List[Tweet]:
        tweets_text = self.get_tweets()
        print(len(tweets_text))
        for tweet in tweets_text:
            status_code = self.__send_tweet_msg__(tweet.content)
            tweet.response_code = status_code

        return tweets_text


class TrumpBotWithMongo(TrumpBotMessenger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_last_ten(self):
        return Tweet.objects.get_last_ten()

    def get_total_tweets(self) -> int:
        return Tweet.objects.count()

    def send_latest_tweets(self):
        min_position = Tweet.objects.get_last_tweet_id()
        self._set_min_position(min_position)
        tweets = super().send_latest_tweets()
        for tweet in tweets:
            print('saved tweet %s' % tweet.tweet_id)
            tweet.save()

        return tweets


class TrumpBotWithAuth(Authentication, TrumpBotWithMongo):
    def __init__(self, auth_file_path='auth.json', *args, **kwargs):
        super().__init__(auth_file_path=auth_file_path, *args, **kwargs)

    # overrides the __send_tweet_msg__ to include auth
    def __send_tweet_msg__(self, content) -> int:
        return self.rebounce_on_401(super().__send_tweet_msg__, content=content, headers=self.get_bearer_header())


class TrumpBot(TrumpBotWithAuth):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TrumpBotScheduler(TrumpBot, BackgroundScheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def start(self, paused=False, seconds=30, **kwargs):
        self.add_job(self.send_latest_tweets, 'interval', seconds=seconds, max_instances=1, **kwargs)
        logging.info('Starting job')
        return super().start(paused=paused)


class TrumpBotTest(TrumpBotScheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __send_tweet_msg__(self, content) -> int:
        print('sent tweet!')
        return 200
