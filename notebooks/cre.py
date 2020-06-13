from functools import partial, reduce
import pandas as pd
from ib_insync import IB, Future, util

# import seaborn as sns
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
import datetime
import pytz

register_matplotlib_converters()

PYTZ_AMS = pytz.timezone("Europe/Amsterdam")
PYTZ_NYC = pytz.timezone("America/New_York")

ib = IB()
ib.connect("127.0.0.1", 4002, clientId=4)  # , GTW=4001, # PAPER=7497

ib.reqMarketDataType(1)

"""
On CME / GLOBEX

Daily settlement of
- S&P/Case-Shiller Home Price Composite Index (CUS)
- Boston Index (BOS)
- Chicago Index (CHI)
- Denver Index (DEN)
- Las Vegas Index (LAV)
- Los Angeles Index (LAX)
- Miami Index (MIA)
- New York Index (NYM)
- San Diego Index (SDG)
- San Francisco Index (SFR)
- Washington DC Index (WDC)

To build a sentiment index
"""

cities = {"BOS": None, "CHI": None, "DEN": None}
for city in cities.keys():

    future = Future(city, exchange="GLOBEX", currency="USD")
    active_futures = ib.reqContractDetails(future)
    future.includeExpired = True
    active_and_expired_futures = ib.reqContractDetails(future)
    expired_futures = [i for i in active_and_expired_futures if i not in active_futures]

    now = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
    durationStr = "300 D"
    barSizeSetting = "1 day"

    d = {}
    for future in active_and_expired_futures:
        lastDate = future.contract.lastTradeDateOrContractMonth
        endDateTime = datetime.datetime.strptime(lastDate, "%Y%m%d").replace(
            tzinfo=datetime.timezone.utc
        )
        if endDateTime > now:
            endDateTime = now
        bars = ib.reqHistoricalData(
            future.contract,
            endDateTime=endDateTime,
            durationStr=durationStr,
            barSizeSetting=barSizeSetting,
            whatToShow="BID_ASK",
            useRTH=True,
            formatDate=2,  # UTC
        )
        if len(bars) > 0:
            bars = util.df(bars)
            bars[lastDate] = bars["close"]
            d[lastDate] = bars[["date", lastDate]]

    df = reduce(partial(pd.merge, on="date", how="outer"), d.values())
    df = df[sorted(df.columns)]
    df = df.set_index("date")
    df = df.sort_values(by="date")
    # df = df.drop_duplicates(keep="first")
    cities[city] = df

fig, ax = plt.subplots()
for e in range(2, len(df.columns[2:-9])):
    expiry = df.columns[e]
    first_quote = df[df[expiry].notna()].index[0]
    sub = df[df.index == first_quote]
    sub = sub[sub.columns[e - 2 : e + 1]]
    ax.plot(sub.columns, sub.values.reshape(3), label=f"Evaluated on: {first_quote}")
    plt.legend()
    plt.title("Boston Index Futures CME")
    plt.xticks(rotation=45)

for first_expiry, last_expiry in zip(df.columns[:-5], df.columns[5:]):
    fig, ax = plt.subplots()
    sub = df[
        (df.index >= pd.to_datetime(first_expiry))
        & (df.index <= pd.to_datetime(last_expiry))
    ]
    curve = sub.head()
    ax.plot(sub.columns, sub.head(1).values.reshape(23), label="Initial curve")
    ax.plot(sub.columns, sub.mean(axis=0).values, label="Smoothed curve")
    ax.fill_between(x=sub.columns, y1=sub.min(axis=0), y2=sub.max(axis=0), color="grey")
    plt.title(f"Last Expiry: {last_expiry}")
    plt.xticks(rotation=45)
    plt.legend()
