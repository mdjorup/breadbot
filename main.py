import time

from account import Account
from bar_socket import GLOBAL_BAR_SOCKET
from market.data_field import DataFieldManager
from market.market_data import MarketData
from trade_socket import GLOBAL_TRADE_SOCKET

stock_symbols = ["AAPL", "MSFT", "GOOGL"]


def initialize_market_data_system():
    # Define the window length for data
    window_length = 30  # Example length

    # Create DataFieldManager for each type of data
    field_managers = [
        DataFieldManager("price", window_length, None),
        DataFieldManager("volume", window_length, None),
    ]

    # Define the stock symbols you are interested in

    # Register these symbols with their respective DataFieldManager
    for symbol in stock_symbols:
        for fm in field_managers:
            fm.register_symbol(symbol)

    # Set up the MarketData with the managers
    market_data = MarketData(window_length)
    for fm in field_managers:
        market_data.add_field(fm)

    return market_data


market_data = initialize_market_data_system()
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
