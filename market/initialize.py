from typing import List

from market.data_field import DataFieldManager
from market.market_data import MarketData
from market.simple_fields import (
    ClosePriceField,
    ExponentialMovingAverageField,
    HighPriceField,
    LowPriceField,
    MACDFIeld,
    MovingAverageField,
    OpenPriceField,
    RSIField,
    VolumeField,
)


def initialize_market_data_system(stock_symbols: List[str]):
    # Define the window length for data
    window_length = 10  # Example length

    # Create DataFieldManager for each type of data
    field_managers = [
        DataFieldManager("Open", window_length, OpenPriceField),
        DataFieldManager("Low", window_length, LowPriceField),
        DataFieldManager("High", window_length, HighPriceField),
        DataFieldManager("Close", window_length, ClosePriceField),
        DataFieldManager("Volume", window_length, VolumeField),
        DataFieldManager("SMA10", window_length, MovingAverageField, 10),
        DataFieldManager("SMA30", window_length, MovingAverageField, 30),
        DataFieldManager("EMA10", window_length, ExponentialMovingAverageField, 10),
        DataFieldManager("RSI", window_length, RSIField, 14),
        DataFieldManager("MACD", window_length, MACDFIeld),
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
