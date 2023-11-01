import os
import time

from alpaca.trading.enums import OrderSide

from account import Account
from market.initialize import initialize_market_data_system
from sockets.bar_socket import GLOBAL_BAR_SOCKET
from sockets.trade_socket import GLOBAL_TRADE_SOCKET

stock_symbols = ["AAPL", "TSLA"]

market_data = initialize_market_data_system(stock_symbols)

for symbol in stock_symbols:
    GLOBAL_BAR_SOCKET.subscribe_to_symbol(symbol)

account = Account()

GLOBAL_TRADE_SOCKET.run()
GLOBAL_BAR_SOCKET.run()

account.trade("AAPL", 40, OrderSide.BUY)
account.trade("AAPL", 30, OrderSide.SELL)
account.trade("TSLA", 10, OrderSide.BUY)
account.trade("TSLA", 10, OrderSide.SELL)
account.trade("AAPL", 10, OrderSide.BUY)
account.trade("TSLA", 10, OrderSide.BUY)

account.print_account_positions()

GLOBAL_TRADE_SOCKET.stop()
GLOBAL_BAR_SOCKET.stop()
