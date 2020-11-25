from ib_insync import *

us_indices = [
    Index("SPX", conId=416904, exchange="CBOE", currency="USD"),
    Index("NQ", conId=11004958, exchange="GLOBEX", currency="USD"),
    Stock("SPY", conId=756733, exchange="SMART", currency="USD"),
    Stock("QQQ", conId=320227571, exchange="SMART", currency="USD"),
    Stock("XLF", conId=4215220, exchange="SMART", currency="USD"),
    Stock("IWC", conId=35445810, exchange="SMART", currency="USD"),
]

us_stocks = [
    Stock(conId=3691937, symbol='AMZN', exchange='SMART', primaryExchange='NASDAQ', currency='USD'),
    Stock(conId=265598, symbol='AAPL', exchange='SMART', primaryExchange='NASDAQ', currency='USD' ),
    Stock(conId=272093, symbol='MSFT', exchange='SMART', primaryExchange='NASDAQ', currency='USD' ),
    Stock(conId=361181057, symbol='ZM', exchange='SMART', primaryExchange='NASDAQ', currency='USD'),
    Stock(conId=371114955, symbol='WORK', exchange='AMEX', primaryExchange='NYSE', currency='USD' ),
    Stock(conId=76792991, symbol='TSLA', exchange='SMART', primaryExchange='NASDAQ', currency='USD'),
    Stock(conId=4627828, symbol='GS', exchange='SMART', primaryExchange='NYSE', currency='USD'),
    Stock(conId=1520593, symbol='JPM', exchange='SMART', primaryExchange='NYSE', currency='USD'),
    Stock(conId=2841574, symbol='MS', exchange='SMART', primaryExchange='NYSE', currency='USD'),
]
