import ssl
from enum import Enum
from typing import List
_create_unverified_https_context = ssl._create_unverified_context

import textblob.download_corpora # lgtm [py/unused-import]
from textblob import TextBlob

from .models import Tweet


class SentimentTone(Enum):
    NEGATIVE = 'negative'
    POSITIVE = 'positive'
    NEUTRAL = 'neutral'


class Sentiment(TextBlob):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.polarity = self.sentiment.polarity
        self.subjectivity = self.sentiment.subjectivity

    def get_tone(self) -> SentimentTone:
        if self.polarity > 0: 
            return SentimentTone.POSITIVE
        elif self.polarity == 0: 
            return SentimentTone.NEUTRAL
        else: 
            return SentimentTone.NEGATIVE

    def get_tone_value(self) -> str:
        return self.get_tone().value


class SentimentWithHistory(Sentiment):
    def __init__(self, *args, **kwargs):
        super().__init__('', *args, **kwargs)

    def __get_tweets__(self) -> List[Tweet]:
        return Tweet.objects.get_tweets_from_today()    

    def _get_average_polarity(self) -> float:
        polarities = [Sentiment(tweet.content).polarity for tweet in self.__get_tweets__()]
        return sum(polarities) / len(polarities)

    def get_todays_tone(self) -> SentimentTone:
        self.polarity = self._get_average_polarity()
        return self.get_tone()

    def get_todays_tone_value(self) -> str:
        return self.get_todays_tone().value


class OverallSentiment(SentimentWithHistory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __get_tweets__(self):
        return Tweet.objects.all()