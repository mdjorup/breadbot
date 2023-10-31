from dataclasses import dataclass
from datetime import datetime

from alpaca.trading.enums import OrderSide

from shared import Bar, Trade
from sockets.bar_socket import BarSubscriber
from sockets.trade_socket import TradeSubscriber


# TODO: do average price per share tracking based on trades that come in
class Position(TradeSubscriber, BarSubscriber):
    def __init__(self, ticker: str, qty: float, price: float) -> None:
        self.symbol = ticker
        self.qty = qty
        self.price = price

        self.trades: list[Trade] = []

    def __repr__(self) -> str:
        return f"{self.symbol} {self.qty} {self.price}"

    def update_trade(self, trade: Trade):
        if trade.symbol != self.symbol:
            return

        print("Updating position " + repr(trade))
        self.trades.append(trade)
        if trade.side == OrderSide.BUY:
            self.qty += trade.qty
        elif trade.side == OrderSide.SELL:
            self.qty -= trade.qty

        self.price = trade.price

    def update_bar(self, bar: Bar):
        if bar.symbol != self.symbol:
            return

        print("Updating position " + repr(bar))
        self.price = bar.close

    def value(self):
        return self.qty * self.price


class CashPosition(Position):
    def __init__(self, ticker: str, qty: float, price: float) -> None:
        super().__init__(ticker, qty, price)
        self.symbol = "$"
        self.qty = qty
        self.price = 1

    def update_trade(self, trade: Trade):
        if trade.side == OrderSide.BUY:
            self.qty -= trade.qty * trade.price
        elif trade.side == OrderSide.SELL:
            self.qty += trade.qty * trade.price
