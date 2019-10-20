from graphene import ObjectType, String, Schema, Boolean
from graphene import DateTime, Int, Field, List, Float

from .models import Tweet
from .sentiment import Sentiment, SentimentWithHistory, OverallSentiment


class SentimentObj(ObjectType):
    percentage = Float()
    tone = String()


class TweetObj(ObjectType):
    date_created = DateTime()
    response_code = Int()
    content = String()
    tweet_id = String()
    sentiment = Field(SentimentObj)

    def resolve_sentiment(self, info):
        s = Sentiment(self.content)
        return SentimentObj(tone=s.get_tone_value(), percentage=s.polarity)


class SentimentQuery(ObjectType):
    todays_sentiment = Field(SentimentObj, description='Returns the overall sentiment of today\'s tweets')
    overall_sentiment = Field(SentimentObj, description='Returns the overall sentiment for all tweets')

    def resolve_todays_sentiment(self, info):
        s = SentimentWithHistory()
        return SentimentObj(tone=s.get_todays_tone_value(), percentage=s.polarity)

    def resolve_overall_sentiment(self, info):
        s = OverallSentiment()
        return SentimentObj(tone=s.get_todays_tone_value(), percentage=s.polarity)


class TwitterQuery(ObjectType):
    tweet_by_id = Field(TweetObj, tweet_id=String(required=True))
    tweets = List(TweetObj, only_today=Boolean(default_value=True))
    
    def resolve_hello(self, info, name):
        return 'Hello %s' % name

    def resolve_tweet_by_id(self, info, tweet_id):
        tweet = Tweet.objects.get_by_tweet_id(int(tweet_id))
        return TweetObj(**tweet.serialize()) if tweet is not None else TweetObj()

    def resolve_tweets(self, info, only_today):
        if only_today:
            tweets = Tweet.objects.get_tweets_from_today()
        else:
            tweets = Tweet.objects.all()
        return [
            TweetObj(**tweet.serialize()) for tweet in tweets
        ]


class Query(TwitterQuery, SentimentQuery, ObjectType):
    pass


schema = Schema(query=Query)