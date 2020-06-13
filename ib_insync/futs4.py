import datetime
from ib_insync import Future
from gulo.get_hist_data.get_hist_ticks import get_hist_ticks
from gulo.utils.utils import start_ib

# contracts = ib.reqContractDetails(Future("MNQ", exchange="GLOBEX", includeExpired=True))
clientId = 3
timeout = 15

ib = start_ib(clientId=clientId, timeout=timeout)

contract = Future(
    conId=362702815,
    symbol="MNQ",
    lastTradeDateOrContractMonth="20190621",
    exchange="GLOBEX",
)
startDateTime: datetime.datetime = datetime.datetime(2019, 3, 20).replace(
    tzinfo=datetime.timezone.utc
)
get_hist_ticks(ib, clientId, timeout, contract, startDateTime)
