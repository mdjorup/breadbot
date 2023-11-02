import asyncio
import os
import time
from datetime import datetime

import numpy as np
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

for _ in range(60):
    asyncio.run(
        GLOBAL_BAR_SOCKET.update_all(
            {
                "symbol": "AAPL",
                "open": 130 + np.random.normal(0, 1),
                "high": 130 + np.random.normal(0, 1),
                "low": 130 + np.random.normal(0, 1),
                "close": 130 + np.random.normal(0, 1),
                "volume": 1000000 + int(np.random.normal(0, 100000)),
                "timestamp": datetime.now(),
            }
        )
    )

account.print_account_positions()

aapl_state = market_data.state("AAPL")
for obs in aapl_state:
    print(obs)


GLOBAL_TRADE_SOCKET.stop()
GLOBAL_BAR_SOCKET.stop()
