from graphene import ObjectType, String, Schema
from graphene import DateTime, Int, Field, List, Float

from .models import Tweet


class Sentiment(ObjectType):
    percentage = Float()
    name = String()


class TweetObj(ObjectType):
    date_created = DateTime()
    response_code = Int()
    content = String()
    tweet_id = String()
    sentiment = Field(Sentiment)

    def resolve_sentiment(self, info):
        return Sentiment(name='happy')


class TwitterQuery(ObjectType):
    tweet = Field(TweetObj, tweet_id=String())
    tweets = List(TweetObj)
    
    def resolve_hello(self, info, name):
        return 'Hello %s' % name

    def resolve_tweet(self, info, tweet_id):
        tweet = Tweet.objects.get_by_tweet_id(int(tweet_id))
        return TweetObj(**tweet.serialize()) if tweet is not None else TweetObj()

    def resolve_tweets(self, info):
        tweets = Tweet.objects.all()
        return [
            TweetObj(**tweet.serialize()) for tweet in tweets
        ]


class Query(TwitterQuery, ObjectType):
    pass


schema = Schema(query=Query)