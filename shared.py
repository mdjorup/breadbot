from dataclasses import dataclass
from datetime import datetime

from alpaca.trading.enums import OrderSide


@dataclass
class Bar:
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: str  # might change

    def __repr__(self) -> str:
        return f"{self.symbol}\t{self.open}\t{self.high}\t{self.low}\t{self.close}\t{self.volume}\t{self.timestamp}"


@dataclass
class Trade:
    side: OrderSide
    symbol: str
    qty: float
    price: float
    timestamp: datetime

    def __repr__(self) -> str:
        return (
            f"{self.side}\t{self.symbol}\t{self.qty}\t${self.price}\t{self.timestamp}"
        )
