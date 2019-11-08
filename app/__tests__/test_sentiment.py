import logging

import pytest

import app.sentiment
from app.sentiment import (
    Sentiment, 
    OverallSentiment, 
    SentimentWithHistory,
    SentimentTone
)

class TweetObj:
    def __init__(self, content, *args, **kwargs):
        self.content = content

class TweetObjects:
    def __init__(self, tone=SentimentTone.POSITIVE, *args, **kwargs):
        self.tone = tone
        self._happy = [
            TweetObj('happy'), TweetObj('congratulations')
        ]
        self._sad = [
            TweetObj('sad'), TweetObj('sorry')
        ]
        self._neutral = [TweetObj('')]

    def all(self):
        return [*self._happy, *self._sad, *self._neutral]

    def get_tweets_from_today(self):
        if self.tone == SentimentTone.NEGATIVE or \
           self.tone == SentimentTone.NEGATIVE.value:
            return self._sad
        elif self.tone == SentimentTone.POSITIVE or \
             self.tone == SentimentTone.POSITIVE.value:
            return self._happy
        else:
            return self._neutral


@pytest.fixture
def sentiment_service():
    yield Sentiment()


@pytest.fixture
def overall_sentiment_service():
    yield OverallSentiment()


@pytest.fixture
def sentiment_with_history_service():
    yield SentimentWithHistory()


@pytest.fixture
def mock_tweets_get_all(monkeypatch):
    class Tweet:
        objects = TweetObjects()

    monkeypatch.setattr(app.sentiment, 'Tweet', Tweet)


@pytest.fixture
def mock_tweets_get_tweets_from_today_happy(monkeypatch):
    class Tweet:
        objects = TweetObjects(SentimentTone.POSITIVE)

    monkeypatch.setattr(app.sentiment, 'Tweet', Tweet)


@pytest.fixture
def mock_tweets_get_tweets_from_today_negative(monkeypatch):
    class Tweet:
        objects = TweetObjects(SentimentTone.NEGATIVE)

    monkeypatch.setattr(app.sentiment, 'Tweet', Tweet)


@pytest.fixture
def mock_tweets_get_tweets_from_today_neutral(monkeypatch):
    class Tweet:
        objects = TweetObjects(SentimentTone.NEUTRAL)

    monkeypatch.setattr(app.sentiment, 'Tweet', Tweet)


def test_sentiment_get_tone():
    test_table = [
        {'value': '', 'expect': SentimentTone.NEUTRAL},
        {'value': 'happy', 'expect': SentimentTone.POSITIVE},
        {'value': 'sad', 'expect': SentimentTone.NEGATIVE}
    ]

    for test in test_table:
        sentiment = Sentiment(test['value'])
        assert sentiment.get_tone() == test['expect']
        assert sentiment.polarity is not None
        assert sentiment.subjectivity is not None


def test_sentiment_get_value():
    test_table = [
        {'value': '', 'expect': SentimentTone.NEUTRAL.value},
        {'value': 'happy', 'expect': SentimentTone.POSITIVE.value},
        {'value': 'sad', 'expect': SentimentTone.NEGATIVE.value}
    ]

    for test in test_table:
        sentiment = Sentiment(test['value'])
        assert sentiment.get_tone_value() == test['expect']
        assert sentiment.polarity is not None
        assert sentiment.subjectivity is not None


def test_get_average_polarity_happy(mock_tweets_get_tweets_from_today_happy,
                                    sentiment_with_history_service):
    tone = sentiment_with_history_service._get_average_polarity()
    assert tone is not None
    assert isinstance(tone, float)
    assert tone > 0


def test_get_average_polarity_negative(mock_tweets_get_tweets_from_today_negative,
                                       sentiment_with_history_service):
    tone = sentiment_with_history_service._get_average_polarity()
    assert tone is not None
    assert isinstance(tone, float)
    assert tone < 0


def test_get_average_polarity_neutral(mock_tweets_get_tweets_from_today_neutral,
                                      sentiment_with_history_service):
    tone = sentiment_with_history_service._get_average_polarity()
    assert tone is not None
    assert isinstance(tone, float)
    assert tone == 0


def test_sentiment_with_history_negative(mock_tweets_get_tweets_from_today_negative,
                                         sentiment_with_history_service):
    tone = sentiment_with_history_service.get_todays_tone()
    tone_value = sentiment_with_history_service.get_todays_tone_value()
    assert tone == SentimentTone.NEGATIVE
    assert tone_value == SentimentTone.NEGATIVE.value


def test_sentiment_with_history_positive(mock_tweets_get_tweets_from_today_happy,
                                         sentiment_with_history_service):
    tone = sentiment_with_history_service.get_todays_tone()
    tone_value = sentiment_with_history_service.get_todays_tone_value()
    assert tone == SentimentTone.POSITIVE
    assert tone_value == SentimentTone.POSITIVE.value


def test_sentiment_with_history_neutral(mock_tweets_get_tweets_from_today_negative,
                                        sentiment_with_history_service):
    tone = sentiment_with_history_service.get_todays_tone()
    tone_value = sentiment_with_history_service.get_todays_tone_value()
    assert tone == SentimentTone.NEGATIVE
    assert tone_value == SentimentTone.NEGATIVE.value


def test_overall_sentiment(mock_tweets_get_all, overall_sentiment_service):
    tone_value = overall_sentiment_service.get_todays_tone_value()
    assert tone_value is not None
    assert tone_value != ""
