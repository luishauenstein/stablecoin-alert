# service for regularly checking latest stablecoin prices and triggering tweet in case something has changed
import yaml
import requests
import redis

if __name__ == "__main__":
    # get coingecko ids from config file
    with open("coins.yaml", "r") as stream:
        try:
            configData = yaml.safe_load(stream)
            coins = set().union(*(d.keys() for d in configData))  # list of coingecko ids
        except yaml.YAMLError as exc:
            print(exc)

    # fetch data from coingecko
    url = 'https://api.coingecko.com/api/v3/simple/price/'  # coingecko endpoint URL
    params = {
        'ids': ','.join(coins),
        'vs_currencies': 'usd'
    }
    try:
        response = requests.get(url, params)
        if response.status_code != 200:
            raise Exception("Response code is not 200")
        data = response.json()
    except:
        raise Exception("No response from Coingecko API")

    # cache new prices in redis
    # r = redis.Redis(host='localhost', port=6379, db=0)
    # for key in data:
    #     r.hset(key, 'price', data[key]['usd'])
    # print('done')
