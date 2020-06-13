from ib_insync import Future
from gulo.get_hist_data.get_hist_bars import HistoricalBars
from gulo.utils.utils import start_ib


client_id = 1
req_timeout = 1200
ib = start_ib(client_id, timeout=req_timeout)
hb = HistoricalBars(client_id=client_id, req_timeout=req_timeout, ib=ib)

future = Future("ES", exchange="GLOBEX", currency="USD")
active_futures = [c.contract for c in ib.reqContractDetails(future)]
future.includeExpired = True
active_and_expired_futures = [c.contract for c in ib.reqContractDetails(future)]
expired_futures = [c for c in active_and_expired_futures if c not in active_futures]

for contract in active_futures:
    if contract:
        hb.run(
            contract=contract,
            what_to_show="BID_ASK",
            bar_size_setting="1 min",
            duration_str="1 W",
        )
