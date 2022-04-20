# script to check cached values in redis every few hours and give confirmation tweet

import os
from dotenv import load_dotenv
import tweepy
import redis
import yaml

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

api = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_KEY_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

r = redis.Redis(host='localhost', port=6379, db=0)  # redis auth

alert_threshold = 0.02  # how much price has to deviate from peg to trigger alert


def main():
    r.incr('confirm-py')  # increment key by one each time confirm.py runs

    # get coingecko ids from config file
    with open("coins.yaml", "r") as stream:
        try:
            configData = yaml.safe_load(stream)
            coingeckoIDs = [*configData]  # list of coingecko ids
        except yaml.YAMLError as exc:
            print(exc)
    for i in coingeckoIDs:
        if not 1 - alert_threshold <= float(r.get(i)) <= 1 + alert_threshold:
            return 0
        pass
    api.create_tweet(
        text=f'{"✅" * 10}\n\nNo special events.\nAll stablecoins maintaining peg currently.')


if __name__ == "__main__":
    main()
