import argparse

parser = argparse.ArgumentParser(description=r"""
""")

parser.add_argument('-np', '--no-post',
                    dest='send_posts',
                    action='store_true',
                    help='Do not send post requests')

parser.add_argument('-nsb', '--no-sentiment-bot',
                    dest='start_sentiment_bot',
                    action='store_true',
                    help='Do not to start the sentiment bot')

options = parser.parse_args()
print(options.__dict__)
