# service for regularly checking latest stablecoin prices and triggering tweet in case something has changed
import os
import sys
from dotenv import load_dotenv
import tweepy
import math
import yaml
import requests
import redis
import time

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
update_trigger = 0.1  # how much price has to drop further to trigger update


def tweetAlert(tweetType, key, configData, price):
    # runs if stablecoin depegs
    name = configData[key]['name']
    ticker = configData[key]['ticker']
    alertSymbols = '🚨' * min(math.floor(10 * abs(1 - price)) + 1, 10)
    tweetTexts = {
        'depeg': f'{alertSymbols}\n\n{name} (#{ticker}) has lost its peg.\nCurrent price: {price} USD',
        'update': f'{alertSymbols}\n\nPrice update: {name} (#{ticker}) price is now {price} USD.',
        'recovery': f'{"✅" * 10}\n\n{name} (#{ticker}) has recovered.\nCurrent price: {price} USD',
    }
    text = tweetTexts[tweetType]
    api.create_tweet(text=text)


def main():
    r.incr('alert-py')  # increment key by one each time alert.py runs

    # get coingecko ids from config file
    with open(os.path.join(sys.path[0], "coins.yaml"), "r") as stream:
        try:
            configData = yaml.safe_load(stream)
            coingeckoIDs = [*configData]  # list of coingecko ids
        except yaml.YAMLError as exc:
            print(exc)

    # fetch data from coingecko
    url = 'https://api.coingecko.com/api/v3/simple/price/'  # coingecko endpoint URL
    params = {
        'ids': ','.join(coingeckoIDs),
        'vs_currencies': 'usd'
    }
    try:
        response = requests.get(url, params)
        if response.status_code != 200:
            raise Exception("Response code is not 200")
        data = response.json()
    except:
        raise Exception("No response from Coingecko API")

    # iterate over each coin and trigger tweet if needed
    for key in data:
        r.setnx(key, 1)  # set to 1 in redis if key doesn't exist yet
        # read last alerted price from redis (1 if no report)
        last_alerted_price = float(r.get(key))
        price = data[key]['usd']  # get current price from coingecko api data
        if 1 - alert_threshold <= price <= 1 + alert_threshold:
            # logic for coins that are in peg currently
            if last_alerted_price != 1:
                r.set(key, 1)
                tweetAlert('recovery', key, configData,
                           price)  # recovery alert

        else:
            # logic for coins that are not in peg currently
            r.set('timestamp', time.time())  # update timestamp of last depeg
            if last_alerted_price == 1:
                r.set(key, price)
                tweetAlert('depeg', key, configData, price)  # depeg alert
            elif abs(price - last_alerted_price) > update_trigger:
                r.set(key, price)
                tweetAlert('update', key, configData,
                           price)  # price update alert


if __name__ == "__main__":
    main()
