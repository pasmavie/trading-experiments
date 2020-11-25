import datetime
import numpy as np
import matplotlib.pyplot as plt
from ib_insync import Contract, IB, util
from typing import Optional, List, Tuple

def plot_contracts_bars(
    ib: IB,
    contracts: List[Contract],
    end: Optional[datetime.datetime] = None,
    bars_settings: Optional[List[Tuple[str, str]]] = None,
    bar_type: Optional[str] = "TRADES"
):
    if end is None:
        end = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
    if bars_settings is None or len(bars_settings) < 1:
        bars_settings = [
            ("2 Y", "1 day"),
            ("6 M", "4 hours"),
            ("1 W", "10 mins"),
            ("1 D", "1 min"),
        ]
    for durationStr, barSizeSetting in bars_settings:
        fig, ax = plt.subplots(figsize=(24,14))
        for contract in contracts:
            bars = util.df(
                ib.reqHistoricalData(
                    contract,
                    endDateTime=end,
                    durationStr=durationStr,
                    barSizeSetting=barSizeSetting,
                    whatToShow=bar_type,
                    useRTH=True,
                    formatDate=2 # UTC
                )
            )
            ys = np.cumprod(np.insert(1 + np.diff(np.log(bars["close"])), 0, 1))
            xs = bars["date"].values
            ax.plot(xs, ys, label=contract.symbol)
            ax.set_title = f"{durationStr} - {barSizeSetting} bars"
            plt.xticks(rotation=45)
            plt.legend()
