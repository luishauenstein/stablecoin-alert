### Stablecoin Depeg Alert

Twitter Bot alerting users of a stablecoin depeg.

Twitter API v2 is used for tweeting.

Coingecko API is used for getting prices.

Redis is used for caching prices.

Alert.py runs once every minute via cronjob.

Confirm.py runs once every hour via cronjob.
