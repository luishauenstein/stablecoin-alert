# service for regularly checking latest stablecoin prices and triggering tweet in case something has changed
import yaml
import requests

if __name__ == "__main__":
    # get coingecko ids from config file
    with open("coins.yaml", "r") as stream:
        try:
            data = yaml.safe_load(stream)
            coins = [i['coingecko_id'] for i in data]  # list of coingecko ids
        except yaml.YAMLError as exc:
            print(exc)
    url = 'https://api.coingecko.com/api/v3/simple/price/'  # coingecko endpoint URL
    params = {
        'ids': ','.join(coins),
        'vs_currencies': 'usd'
    }
    response = requests.get(url, params)
    print(response.json())

    # import redis
    # r = redis.Redis(host='localhost', port=6379, db=0)
    # r.set('foo', 'bar')
    # print('done')
