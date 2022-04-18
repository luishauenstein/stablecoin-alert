# service for regularly checking latest stablecoin prices and triggering tweet in case something has changed
import requests
url = 'https://api.coingecko.com/api/v3/simple/price/'  # coingecko endpoint URL
coins = ['bitcoin', 'alchemix-usd']  # list of coingecko ids
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
