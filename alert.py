# service for regularly checking latest stablecoin prices and triggering tweet in case something has changed
import yaml
import requests
import redis
import tweepy

r = redis.Redis(host='localhost', port=6379, db=0)  # redis auth
auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret, access_token, access_token_secret
)
api = tweepy.API(auth)  # twitter api auth

alert_threshold = 0.02  # how much price has to deviate from peg to trigger alert
update_trigger = 0.1  # how much price has to drop further to trigger update


def depegAlert(key, price):
    # runs if stablecoin depegs
    print(f'{key} depeg')
    pass


def updateAlert(key, price):
    # runs if price of depeged stablecoin changes significantly
    print(f'{key} update')
    pass


def recoveryAlert(key, price):
    # runs if stablecoin repegs
    print(f'{key} recovery')
    pass


def main():
    # get coingecko ids from config file
    with open("coins.yaml", "r") as stream:
        try:
            configData = yaml.safe_load(stream)
            coingeckoIDs = set().union(*(d.keys()
                                         for d in configData))  # list of coingecko ids
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
                # TRIGGER RECOVERY ALERT
                recoveryAlert(key, price)
                r.set(key, 1)
        else:
            # logic for coins that are not in peg currently
            if last_alerted_price == 1:
                r.set(key, price)
                depegAlert(key, price)
            elif abs(price - last_alerted_price) > update_trigger:
                r.set(key, price)
                updateAlert(key, price)
                pass  # TRIGGER UPDATE


if __name__ == "__main__":
    main()
