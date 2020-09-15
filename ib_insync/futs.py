import datetime
from ib_insync import Future
from gulo.get_hist_data.get_hist_ticks import get_hist_ticks
from gulo.utils.utils import start_ib

# contracts = ib.reqContractDetails(Future("MES", exchange="GLOBEX", includeExpired=True))
client_id = 1
port = 4002
timeout = 15

ib = start_ib(client_id=client_id, port=port, timeout=timeout)

# contract = Future(
#     conId=371749771,
#     symbol="MES",
#     lastTradeDateOrContractMonth="20200918",
#     multiplier="5",
#     exchange="GLOBEX",
#     currency="USD",
#     localSymbol="MESU0",
#     tradingClass="MES",
# )
# contract = Future(conId=362698833, symbol='MES', lastTradeDateOrContractMonth='20200619', multiplier='5', exchange='GLOBEX', currency='USD', localSymbol='MESM0', tradingClass='MES')
# contract = Future(conId=362698381, symbol='MES', lastTradeDateOrContractMonth='20200320', multiplier='5', exchange='GLOBEX', currency='USD', localSymbol='MESH0', tradingClass='MES')
# contract = Future(conId=362699966, symbol='MES', lastTradeDateOrContractMonth='20191220', multiplier='5', exchange='GLOBEX', currency='USD', localSymbol='MESZ9', tradingClass='MES')
# contract = Future(conId=362699593, symbol='MES', lastTradeDateOrContractMonth='20190920', multiplier='5', exchange='GLOBEX', currency='USD', localSymbol='MESU9', tradingClass='MES')
contract = Future(conId=362699310, symbol='MES', lastTradeDateOrContractMonth='20190621', multiplier='5', exchange='GLOBEX', currency='USD', localSymbol='MESM9', tradingClass='MES')
startDateTime: datetime.datetime = datetime.datetime(2019, 3, 20).replace(
    tzinfo=datetime.timezone.utc
)

get_hist_ticks(
    ib=ib,
    client_id=client_id,
    port=port,
    timeout=timeout,
    contract=contract,
    startDateTime=startDateTime,
)
