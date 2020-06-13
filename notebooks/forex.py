from ib_insync import *
import seaborn as sns
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

import datetime
import pytz

PYTZ_AMS = pytz.timezone("Europe/Amsterdam")
PYTZ_NYC = pytz.timezone("America/New_York")

ib = IB()
ib.connect("127.0.0.1", 4002, clientId=2)  # TWS=7496, GTW=4001, # PAPER=7497

ib.reqMarketDataType(1)


settings = [
    ("10 Y", "1 day"),
    ("2 Y", "1 day"),
    ("6 M", "4 hours"),
    ("1 W", "10 mins"),
    ("1 D", "1 min"),
]
END = datetime.datetime.now().replace(tzinfo=pytz.utc)

for duarationStr, barSizeSetting in settings:
    fig, ax = plt.subplots(figsize=(16, 10))
    for pair in ("EURUSD", "GBPUSD", "CHFUSD"):
        bars = ib.reqHistoricalData(
            Forex(pair=pair),
            endDateTime=END,
            durationStr=duarationStr,
            barSizeSetting=barSizeSetting,
            whatToShow="BID_ASK",
            useRTH=False,
            formatDate=2,  # UTC
        )
        bars = util.df(bars)
        bars[pair] = (
            bars["open"] + bars["close"]
        ) / 2  # open=bid and close=ask, check ibkr
        bars.plot(x="date", y=pair, ax=ax)
        ax.fill_between(x="date", y1="low", y2="high", data=bars, color="grey")


#
# GE
#

GEs = ib.reqContractDetails(Future(symbol="GE", exchange="GLOBEX"))
GEs = util.df(sorted(GEs, key=lambda x: x.contract.lastTradeDateOrContractMonth))


def getbars(contract, end):
    x = None
    try:
        bars = ib.reqHistoricalData(
            contract,
            endDateTime=date,
            durationStr="1 D",
            barSizeSetting="1 day",
            whatToShow="TRADES",
            useRTH=False,
            formatDate=2,  # UTC
        )
        df = util.df(bars)
        x = df["average"][0]
    except:
        x = None
    return x


strdates = ("20200517", "20200417", "20200317", "20200217", "20200117")
fig, ax = plt.subplots(figsize=(16, 12))
for strdate in strdates:
    date = datetime.datetime.strptime(strdate, "%Y%m%d").replace(tzinfo=pytz.utc)
    GEs[strdate] = GEs.contract.map(lambda x: getbars(x, date))
    GEs.plot(x="contractMonth", y=strdate, ax=ax)

"""
Fixing Component ===> Description

Fed Funds Effective ===> (USD only) is the volume weighted average of the transactions processed through the Federal Reserve between member banks. It is intended to reflect the best estimate of interbank financing activity for Reserve Bank members and is the reference for many short term money market transactions in the broader market.

LIBOR ===> (multiple currencies) stands for London Inter-Bank Offered Rate. It is a daily fixing for deposits with durations from overnight to 1 year and is determined by a group of large London banks. It is the most widely used measurement for interest rates on most currencies outside the domestic market(s).

EONIA ===> (EUR only) is the global standard for overnight Euro deposits and is determined by a weighted average of the actual transactions between major continental European banks mediated through the European Central Bank.

HIBOR ===> (HKD only) is a daily fixing based on a group of large Hong Kong banks. Similar methods and durations are set as for LIBOR currencies.

KORIBOR ===> (KRW only) is an average of the leading interest rates for KRW as determined by a group of large Korean banks. The benchmark utilizes the KORIBOR with 1 week maturity.

STIBOR ===> (SEK only) is a daily fixing based on a group of large Swedish banks. The same methods and durations are set as for LIBOR currencies.

RUONIA ===> (RUB) is a weighted rate of overnight Ruble loans. The RUONIA is calculated by the Bank of Russia.

PRIBOR ===> (CZK) is the average interest rate at which term deposits are offered between prime banks.

BUBOR ===> (HUF) is the average interest rate at which term deposits are offered between prime banks.

TIIE ===> (MXN only) is the interbank "equilibrium" rate based on the quotes provided by money center banks as calculated by the Mexican Central Bank. The benchmark TIIE is based on 28-day deposits so is atypical as a measure for short term funds (most currencies have an overnight or similar short term benchmark).

Overnight ===> (O/N) rate is the most widely used short term benchmark and represents the rate for balances held from today until the next business day.

Spot-Next ===> (S/N) refers to the rate on balances from the next business day to the business day thereafter. Due to time zone and other criteria, Spot-Next rates are sometimes used as the short-term reference.

RBA Daily Cash Target ===> (AUD) refers to a 1 day rate set by the Reserve Bank of Australia to influence short term interest rates.

NZD Daily Cash Target ===> (NZD) refers to a 1 day rate set by the Reserve Bank of New Zealand to influence short term interest rates.

CNH HIBOR Overnight Fixing Rate ===> For the calculation of interest, IB follows market convention and will not include fixings made on a CNH, CNY or HKD holiday.

Day-Count conventions: ===> IB conforms to the international standards for day-counting wherein deposits rates for most currencies are expressed in terms of a 360 day year, while for other currencies (ex: GBP) the convention is a 365 day year.

Also look to: https://www.interactivebrokers.com/en/index.php?f=701&date=202001&ib_entity=llc
https://www.cmegroup.com/education/articles-and-reports/replicating-otc-fx-market-positions-with-cme-fx-futures.html¶
"""
