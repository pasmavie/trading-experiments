from ib_insync import IB, Stock, Option
import datetime
from typing import List
import pandas as pd
import pytz

"""
A sale's also a buy. How the fuck do I distinguish that shit?
Focus only on opts transacted at the ask. Probably Δ hedged by the writer. What about Γ? EOD?
"""

ib = IB()

ib.connect("127.0.0.1", 4002, clientId=2)  # TWS=7496, GTW=4001, # PAPER=7497

cs = ib.reqContractDetails(Stock(symbol="SPY", exchange="ARCA"))
x = cs[0].contract


# 1) prendi tutti gli strikes e tutte le exp
chains = ib.reqSecDefOptParams(
    underlyingSymbol=x.symbol,
    futFopExchange="",
    underlyingSecType=x.secType,
    underlyingConId=x.conId,
)
chain = next(c for c in chains if c.tradingClass == "SPY" and c.exchange == "SMART")

[ticker] = ib.reqTickers(x)
xValue = ticker.marketPrice()

strikes = [
    strike
    for strike in chain.strikes
    if strike % 5 == 0 and xValue - 2 < strike < xValue + 2
]
expirations = sorted(exp for exp in chain.expirations)[:3]
rights = ["P", "C"]

contracts = [
    Option("SPY", expiration, strike, right, "SMART", tradingClass="SPY")
    for right in rights
    for expiration in expirations
    for strike in strikes
]

contracts = ib.qualifyContracts(*contracts)

# 2) ricevi tickers
# 3) calcola hedge basato su greeks
start = datetime.datetime(2020, 4, 14, 13, 30).replace(tzinfo=pytz.utc)
allticks: List = []
ticks = ib.reqHistoricalTicks(
    contracts[0],
    startDateTime=start,
    endDateTime=None,
    numberOfTicks=1000,
    whatToShow="TRADES",
    ignoreSize=True,
    useRth=True,
)
while 1:
    # ib.waitOnUpdate()
    allticks = allticks + [
        (start, t.time.replace(tzinfo=pytz.utc), t.price, t.size) for t in ticks
    ]
    start = ticks[-1].time + datetime.timedelta(microseconds=1)

df = pd.DataFrame(allticks, columns=["date", "tick", "price", "size"])

es = ib.reqContractDetails(Future(symbol="ES", exchange="GLOBEX"))[0].contract
