import os

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import AssetClass, OrderSide, TimeInForce
from alpaca.trading.models import Order, TradeAccount
from alpaca.trading.requests import MarketOrderRequest
from dotenv import load_dotenv

from bar_socket import GLOBAL_BAR_SOCKET
from position import CashPosition, Position
from trade_socket import GLOBAL_TRADE_SOCKET


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
        self.cash_position = CashPosition("$", 0, 1)
        if isinstance(account, TradeAccount) and account.cash:
            self.cash_position = CashPosition("$", float(account.cash), 1)

        GLOBAL_TRADE_SOCKET.add_subscriber(self.cash_position)

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

    def trade(self, ticker: str, shares: float):
        if ticker not in self.positions:
            new_position = Position(ticker, 0, 0)
            GLOBAL_TRADE_SOCKET.add_subscriber(new_position)
            GLOBAL_BAR_SOCKET.add_subscriber(new_position)
            self.positions[ticker] = new_position

        if shares > 0:
            market_order_data = MarketOrderRequest(
                symbol=ticker,
                qty=shares,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
            )
            market_order = self.trading_client.submit_order(
                order_data=market_order_data
            )
        elif shares < 0:
            market_order_data = MarketOrderRequest(
                symbol=ticker,
                qty=abs(shares),
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
            )
            market_order = self.trading_client.submit_order(
                order_data=market_order_data
            )

    def balance(self):
        return self.cash_position.value() + sum(
            [p.value() for p in self.positions.values()]
        )
