import numpy as np
from ib_insync import Ticker
from typing import Tuple


class FindSales:
    def __init__(self):
        self.sales_tick_type: int = 4

    def ticks_exist(self, ticker: Ticker) -> bool:
        return ticker.ticks is not None

    def build_array(self, ticker: Ticker) -> np.array:
        if self.ticks_exist(ticker):
            ticks = np.array(
                [
                    (t.price, t.size)
                    for t in ticker.ticks
                    if t.tickType == self.sales_tick_type
                ]
            )
        return ticks

    def return_prices_and_sizes(self, ticker: Ticker) -> Tuple[np.array, np.array]:
        prices, sizes = np.empty(0), np.empty(0)
        ticks = self.build_array(ticker)
        if len(ticks) > 0:
            prices = ticks[:, 0]
            sizes = ticks[:, 1]
        return prices, sizes


class NextSignal:
    def __init__(self, size_trigger: float):
        self.size_trigger = size_trigger

    def signal(self, bid: float, ask: float, prices: np.array, sizes: np.array) -> int:
        mask = np.where(sizes > self.size_trigger)
        if len(mask) > 0:
            prices = prices[mask]
            # set 1 where the transaction happened >= ask and -1 where happened close to the bid. 0 elsewhere
            prices = np.where(prices >= ask, 1, np.where(prices <= bid, -1, 0))
            # multiply the directional signal by the size and sum to offset transactions yielding contrasting indicators
            signal = np.sum(prices * sizes[mask])
            # if the final result is > than the min size trigger, yield the signal, stay flat otherwise
        # signal / abs(signal) is used to bring back the signal to the usual +/-1 size
        if abs(signal) >= self.size_trigger:
            signal = signal / abs(signal)
        else:
            signal = 0
        return int(signal)
