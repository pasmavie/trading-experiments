import numpy as np
import pandas as pd
import seaborn as sns

# import datetime
import matplotlib.pyplot as plt
from mlfinlab.data_structures import (
    standard_data_structures,
    get_ema_dollar_imbalance_bars,
    get_const_dollar_imbalance_bars,
)
from scipy import stats
from statsmodels.graphics.tsaplots import plot_acf

# from sklearn.preprocessing import StandardScaler
# from typing import List
from gulo.utils.db import Db

with Db()._conn.cursor() as cur:
    cur.execute("select * from ticks.mnq20200619_362702495;")
    data = cur.fetchall()
contract_unit = 2  # 2$ x handle for MNQ

data = pd.DataFrame(data, columns=["date_time", "price", "volume", "exchange"])
data["date_time"] = pd.to_datetime(data["date_time"], utc=True)
data = data.sort_values("date_time")
data["dollar_value"] = data["price"].values * data["volume"].values
data["day"] = data["date_time"].map(lambda x: x.date())
# data["mins"] = data["date_time"].map(
#     lambda x: x - datetime.timedelta(seconds=60 - x.second) - datetime.timedelta(microseconds=x.microsecond)
# )

# Date bars
grouper = data.groupby(pd.Grouper(key="date_time", freq="15min"))
time_bars = grouper.aggregate(
    open=pd.NamedAgg(column="price", aggfunc="first"),
    close=pd.NamedAgg(column="price", aggfunc="last"),
    cum_buy_volume=pd.NamedAgg(column="volume", aggfunc="sum"),
    cum_dollar_value=pd.NamedAgg(column="dollar_value", aggfunc="sum"),
)
time_bars = time_bars[time_bars["cum_buy_volume"] > 0].copy()
# NO!: time_bars["close"] = time_bars["close"].fillna(method="ffill")
time_bars["returns"] = np.log(time_bars["close"]).diff()

# ~0.34%
print(f"Date bars {len(time_bars)}: {100*len(time_bars) / len(data)}%")

# Tick Bars
tick_bars = standard_data_structures.get_tick_bars(data, threshold=10000)  # ticks
tick_bars["returns"] = np.log(tick_bars["close"]).diff()
print(f"Tick bars {len(tick_bars)}: {100*len(tick_bars) / len(data)}%")

# Dollar Bars
# 1/50 of the avg daily dollar value
dollar_threshold = (
    data.groupby(pd.Grouper(key="date_time", freq="1D")).sum()["dollar_value"].mean()
)
dollar_threshold /= 50
dollar_threshold = int(dollar_threshold)

dollar_bars = standard_data_structures.get_dollar_bars(
    data, threshold=dollar_threshold, verbose=True
)
dollar_bars["returns"] = np.log(dollar_bars["close"]).diff()
print(f"Dollar bars {len(dollar_bars)}: {100*len(dollar_bars) / len(data)}%")

fig, ax = plt.subplots(nrows=3, ncols=3)
for i, j in enumerate(
    zip(("time bars", "tick bars", "dollar bars"), (time_bars, tick_bars, dollar_bars))
):
    l, df = j[0], j[1]
    df["cum_dollar_value"].hist(bins=100, ax=ax[i, 0], label=f"{l} $value")
    df["cum_buy_volume"].hist(bins=100, ax=ax[i, 1], label=f"{l} volume")
    rets = df["returns"].dropna()
    plot_acf(rets, lags=10, zero=False, ax=ax[i, 2], label=f"{l} autocorr")
    ax[i, 0].legend()
    ax[i, 1].legend()
    ax[i, 2].legend()


fig2, ax2 = plt.subplots(figsize=(16, 10))
jbs = {}
for i, j in enumerate(
    zip(("time bars", "tick bars", "dollar bars"), (time_bars, tick_bars, dollar_bars))
):
    l, df = j[0], j[1]
    rets = df["returns"].dropna()
    jbs[l] = int(stats.jarque_bera(rets)[0])  # lower is more normal
    std_rets = (rets - rets.mean()) / rets.std()
    sns.kdeplot(std_rets, label=f"{l}", linewidth=2, ax=ax2)
    sns.kdeplot(
        np.random.normal(size=len(df)), label=f"{l} Normal", linestyle="--", ax=ax2
    )
ax2.set_title(
    f"Normality. Jarque-Bera: {sorted(jbs.items(), key=lambda item: item[1])}"
)
plt.show()


# EMA, Const Dollar Imbalance Bars
dollar_imbalance_ema = get_ema_dollar_imbalance_bars(data)
dollar_imbalance_const = get_const_dollar_imbalance_bars(data)
