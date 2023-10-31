import time

from account import Account
from market.initialize import initialize_market_data_system
from sockets.bar_socket import GLOBAL_BAR_SOCKET
from sockets.trade_socket import GLOBAL_TRADE_SOCKET

stock_symbols = ["AAPL", "MSFT", "GOOGL"]

market_data = initialize_market_data_system(stock_symbols)


account = Account()


GLOBAL_TRADE_SOCKET.run()
GLOBAL_BAR_SOCKET.run()

for symbol in stock_symbols:
    GLOBAL_BAR_SOCKET.subscribe_to_symbol(symbol)

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
