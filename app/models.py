import os
import datetime

import mongoengine as mongo

mongo_url = os.environ.get('MONGO_DB_URL')
mongo_db = os.environ.get('MONGO_DB_NAME', 0)

print(mongo_url)

mongo.connect(mongo_db, host=mongo_url)


class TweetQuerySet(mongo.QuerySet):

    def get_all(self):
        return self.all()

    def get_last_ten(self):
        return self.all()[:10]

    def get_last_tweet_id(self) -> int:
        tweet = self.order_by('-tweet_id').limit(1).first()
        return tweet.tweet_id if tweet is not None else 1111111

    def ordered(self):
        return self.order_by('-tweet_id').all()

    def get_all_bad_responses(self):
        return self.filter(response_code__gt=201)

    def get_filtered_tweets(self):
        return self.only('date_created', 'response_code', 'content', 'tweet_id')


class Tweet(mongo.Document):
    date_created = mongo.DateTimeField(default=datetime.datetime.utcnow)
    response_code = mongo.IntField(required=True, default=404)
    content = mongo.StringField(required=True)
    tweet_id = mongo.IntField(required=True)

    meta = {'queryset_class' : TweetQuerySet}

    def serialize(self):
        return {
            'date_created': self.date_created,
            'response_code': self.response_code,
            'content': self.content,
            'tweet_id': self.tweet_id
        }
