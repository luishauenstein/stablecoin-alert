# service for regularly checking latest stablecoin prices and triggering tweet in case something has changed
import os
from dotenv import load_dotenv
import tweepy
import yaml
import requests
import redis

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuth1UserHandler(
    API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
)
api = tweepy.API(auth)  # twitter api auth

r = redis.Redis(host='localhost', port=6379, db=0)  # redis auth

alert_threshold = 0.02  # how much price has to deviate from peg to trigger alert
update_trigger = 0.1  # how much price has to drop further to trigger update


def tweetAlert(tweetType, key, configData, price):
    # runs if stablecoin depegs
    name = configData[key]['name']
    ticker = configData[key]['ticker']
    alertSymbols = '🚨' * 3
    tweetTexts = {
        'depeg': f'{alertSymbols}\n{name} (#{ticker}) has lost its peg.\nCurrent price: {price} USD',
        'update': f'{alertSymbols}\nPrice update: {name} (#{ticker}) price is now {price} USD.',
        'recovery': f'{alertSymbols}\n{name} (#{ticker}) has recovered.\nCurrent price: {price} USD',
    }
    text = tweetTexts[tweetType]
    print(text)
    # tweepy.Client.create_tweet(text=text)


def main():
    # get coingecko ids from config file
    with open("coins.yaml", "r") as stream:
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
        r.setnx(key, 1)  # set to 1 if key doesn't exist yet
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
            if last_alerted_price == 1:
                r.set(key, price)
                tweetAlert('depeg', key, configData, price)  # depeg alert
            elif abs(price - last_alerted_price) > update_trigger:
                r.set(key, price)
                tweetAlert('update', key, configData,
                           price)  # price update alert


if __name__ == "__main__":
    main()
