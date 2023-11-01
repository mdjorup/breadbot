import asyncio
import os
from datetime import datetime

import numpy as np
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import AssetClass, OrderSide, TimeInForce
from alpaca.trading.models import Order, TradeAccount
from alpaca.trading.requests import MarketOrderRequest
from dotenv import load_dotenv

from position import CashPosition, Position
from sockets.bar_socket import GLOBAL_BAR_SOCKET
from sockets.trade_socket import GLOBAL_TRADE_SOCKET


class Account:
    def __init__(self) -> None:
        load_dotenv()
        self.trading_client = TradingClient(
            os.environ.get("ALPACA_KEY"),
            os.environ.get("ALPACA_SECRET"),
            paper=True,
        )

        account = self.trading_client.get_account()
        positions = self.trading_client.get_all_positions()

        self.positions = {}
        self.cash_position = CashPosition("$", 100000, 1)

        if os.environ.get("ENV", "") == "prod":
            if isinstance(account, TradeAccount) and account.cash:
                self.cash_position = CashPosition("$", float(account.cash), 1)

            if isinstance(positions, list):
                for position in positions:
                    if (
                        position.asset_class == AssetClass.US_EQUITY
                        and position.current_price
                    ):
                        new_position = Position(
                            position.symbol,
                            float(position.qty),
                            float(position.current_price),
                        )

                        GLOBAL_TRADE_SOCKET.add_subscriber(new_position)
                        GLOBAL_BAR_SOCKET.add_subscriber(new_position)
                        self.positions[position.symbol] = new_position

        GLOBAL_TRADE_SOCKET.add_subscriber(self.cash_position)

    def trade(self, ticker: str, shares: float, order_side: OrderSide):
        if ticker not in self.positions:
            new_position = Position(ticker, 0, 0)
            GLOBAL_TRADE_SOCKET.add_subscriber(new_position)
            GLOBAL_BAR_SOCKET.add_subscriber(new_position)
            self.positions[ticker] = new_position

        shares = abs(shares)

        if os.environ.get("ENV", "") == "prod":
            self.__trade_prod(ticker, shares, order_side)
        else:
            self.__trade_dev(ticker, shares, order_side)

    def __trade_prod(self, ticker: str, shares: float, order_side: OrderSide):
        market_order_data = MarketOrderRequest(
            symbol=ticker,
            qty=shares,
            side=order_side,
            time_in_force=TimeInForce.DAY,
        )
        market_order = self.trading_client.submit_order(order_data=market_order_data)

    def __trade_dev(self, ticker: str, shares: float, order_side: OrderSide):
        asyncio.run(
            GLOBAL_TRADE_SOCKET.update_all(
                {
                    "qty": shares,
                    "price": 130 + np.random.normal(0, 1),
                    "order": {
                        "side": order_side,
                        "symbol": ticker,
                    },
                    "timestamp": datetime.now(),
                }
            )
        )

    def balance(self):
        return self.cash_position.value() + sum(
            [p.value() for p in self.positions.values()]
        )

    def print_account_positions(self):
        print("Positions:")
        for k, v in self.positions.items():
            print(f"{k}: {v}")
        print(f"Cash: {self.cash_position.value()}")
        print(f"Total: {self.balance()}")
