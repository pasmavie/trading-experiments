import numpy as np
from ib_insync import IB, Future, Order, Trade
from typing import List, Union
from options import FindSales, NextSignal


class DocStrat:
    def __init__(self, ib, es: Future, mes: Future):
        self.ib = ib
        self.es = es
        self.mes = mes
        # TODO: add SPY and SPX options?
        self.total_quantity = 1
        self.trade: Trade = None
        self.stop_loss: Trade = None
        self.take_profit: Trade = None
        self.position: str = "FLAT"
        self.ib_actions = {1: "BUY", -1: "SELL"}

    def order(self, ticker, signal, stop_loss_handles=2, take_profit_handles=2):
        """
        Create orders from signal. Could become a @staticmethod without the assert and ib_actions.
        But consider the opposite (having the handles as class params) to eas hyperparam tuning.
        """
        action = self.ib_actions[signal]
        if action == "BUY":
            reverse = "SELL"
            lmt = ticker.ask
            cancel_f = (
                lambda order, ticker: True
                if order.order.lmtPrice < ticker.ask - 0.25  # Small buffer
                else False
            )
            take_profit = lmt + take_profit_handles
        elif action == "SELL":
            reverse = "BUY"
            lmt = ticker.bid
            cancel_f = (
                lambda order, ticker: True
                if order.order.lmtPrice > ticker.bid + 0.25  # Small buffer
                else False
            )
            take_profit = lmt - take_profit_handles
        order = Order(
            action=action,
            orderType="LMT",
            totalQuantity=self.total_quantity,
            lmtPrice=lmt,
            outsideRth=True,
        )
        stop_loss_order = Order(
            action=reverse,
            orderType="TRAIL",
            totalQuantity=self.total_quantity,
            # TrailStopPRice causes troubles
            auxPrice=stop_loss_handles,
            outsideRth=True,
        )
        take_profit_order = Order(
            action=reverse,
            orderType="LMT",
            totalQuantity=self.total_quantity,
            lmtPrice=take_profit,
            outsideRth=True,
        )
        return order, stop_loss_order, take_profit_order, cancel_f

    def emergency_exit(self, asset, signal):
        """
        Blocking
        """
        if self.take_profit.order:
            self.ib.cancelOrder(self.take_profit.order)
        if self.stop_loss.order:
            self.ib.cancelOrder(self.stop_loss.order)
        action = self.ib_actions[signal]
        emergency_exit = self.ib.placeOrder(
            asset,
            Order(
                action=action,
                orderType="MKT",
                totalQuantity=self.total_quantity,
                outsideRth=True,
            ),
        )
        # blocking
        while not emergency_exit.isDone():
            self.ib.waitOnUpdate()
        self.trade = None
        self.stop_loss = None
        self.take_profit = None

    @staticmethod
    def healthcheck_trades(trades: Union[Trade, List[Trade]]) -> bool:
        if type(trades) == Trade:
            trades = [trades]
        for trade in trades:
            if trade.orderStatus.status == "Cancelled":
                return False
        return True

    def cancel_order(self, order):
        cancel = self.ib.cancelOrder(order)
        while not cancel.isDone():
            self.ib.waitOnUpdate()
        self.trade = None
        self.stop_loss = None
        self.take_profit = None

    def adverse_signal(self, signal: int) -> bool:
        assertion: bool = False
        if signal != 0:
            assertion = self.ib_actions[signal] != self.trade.order.action
        return assertion

    def run(self):
        # subscribe to real time mkt data
        ticker_es = self.ib.reqMktData(
            self.es, genericTickList="233"
        )  # https://interactivebrokers.github.io/tws-api/tick_types.html
        # ticker_mes = self.ib.reqMktData(self.mes)
        while 1:
            ib.waitOnUpdate()

            prices, sizes = FindSales().return_prices_and_sizes(ticker_es)
            # evaluate the transactions (if any) and eventually output a signal (or None)
            signal: int = 0
            if np.sum(np.isnan(prices)) == 0:
                signal = NextSignal(size_trigger=100).signal(
                    ticker_es.bid, ticker_es.ask, prices, sizes
                )

            if not self.trade and signal != 0:  # you can start a new trade
                order, stop_loss_order, take_profit_order, cancel_f = self.order(
                    ticker_es, signal
                )
                self.trade = self.ib.placeOrder(self.es, order)
                # note, stop_loss and take_profit won't be opened until the trade.isDone
                # this won't happen until the next loop iteration at least
                # but I should be able to check if the order is good immediately
                if not self.healthcheck_trades(self.trade):
                    self.trade = None
                logger.debug("---------------TRADE--------------------------")
                logger.debug(f"{ticker_es.bid} / {ticker_es.ask}")
                logger.debug(f"{prices} / {sizes}")
                logger.debug(f"{self.trade.order}")
                logger.debug("----------------------------------------------")

            elif self.trade:  # gotta handle the open trade
                adverse_signal = self.adverse_signal(signal)
                order_slipped = cancel_f(self.trade, ticker_es)
                # first of all check that the last signal agrees with your position
                if not self.trade.isDone():
                    if order_slipped or adverse_signal:
                        self.cancel_order(self.trade.order)  # blocking
                        logger.debug(f"Cancel F: {order_slipped}")
                        logger.debug(f"Adverse Signal: {adverse_signal}")
                        logger.debug(f"{ticker_es.bid} / {ticker_es.ask}")
                        logger.debug("Order canceled")
                        logger.debug("----------------------------------------------")

                # if we get a adverse signal we have to close immediately
                elif (
                    adverse_signal
                ):  # note that is used when the trade isn't done as well
                    self.emergency_exit(self.es, signal)  # blocking
                    logger.debug(f"{ticker_es.bid} / {ticker_es.ask}")
                    logger.debug("Adverse signal. Exit trade")
                    logger.debug("----------------------------------------------")

                # otherwise, if the trade went through and all is fine, you can place the two auxiliary orders
                elif not self.stop_loss:
                    self.stop_loss = self.ib.placeOrder(self.es, stop_loss_order)
                    self.take_profit = self.ib.placeOrder(self.es, take_profit_order)
                    logger.debug("Order filled, opened stop_loss and take_profit")
                    logger.debug(f"{self.trade.orderStatus}")
                    logger.debug(f"{self.stop_loss.order}")
                    logger.debug(f"{self.take_profit.order}")
                    logger.debug("----------------------------------------------")

                elif not self.healthcheck_trades([self.stop_loss, self.take_profit]):
                    self.emergency_exit(self.es, stop_loss_order.action)
                    logger.debug("Take profit or Stop loss failed: Emergency exit.")
                    logger.debug("----------------------------------------------")

                elif self.stop_loss.isDone():
                    logger.debug(f"{ticker_es.bid} / {ticker_es.ask}")
                    logger.debug("Hit stop loss")
                    logger.debug(f"{self.stop_loss}")
                    logger.debug("----------------------------------------------")
                    self.cancel_order(self.take_profit.order)

                elif self.take_profit.isDone():
                    logger.debug(f"{ticker_es.bid} / {ticker_es.ask}")
                    logger.debug("Hit take profit")
                    logger.debug(f"{self.take_profit}")
                    logger.debug("----------------------------------------------")
                    self.cancel_order(self.stop_loss.order)


if __name__ == "__main__":
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.addHandler(logging.FileHandler("trades.log"))

    ib = IB()
    ib.connect("127.0.0.1", 4002, clientId=1)  # TWS=7496, PAPER=7497, GTW=4001
    ib.reqMarketDataType(1)

    # this isn't a proper way to roll the fucking futures
    ES = ib.reqContractDetails(Future(symbol="ES", exchange="GLOBEX"))[0].contract
    MES = ib.reqContractDetails(Future(symbol="MES", exchange="GLOBEX"))[0].contract

    ds = DocStrat(ib=ib, es=ES, mes=MES)

    logger.debug("Doc Strategy instantiated")
    ds.run()
