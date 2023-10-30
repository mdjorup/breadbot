import time

from account import Account
from bar_socket import GLOBAL_BAR_SOCKET
from trade_socket import GLOBAL_TRADE_SOCKET

account = Account()

GLOBAL_TRADE_SOCKET.run()
GLOBAL_BAR_SOCKET.subscribe_to_symbol("AAPL")
GLOBAL_BAR_SOCKET.subscribe_to_symbol("TSLA")

GLOBAL_BAR_SOCKET.run()

account.trade("AAPL", 87)

time.sleep(5)

print(account.balance())

for k, v in account.positions.items():
    print(f"{k}: {v}")

account.trade("AAPL", -87)

time.sleep(30)

print(account.balance())

GLOBAL_TRADE_SOCKET.stop()

GLOBAL_BAR_SOCKET.stop()

print(account.balance())
