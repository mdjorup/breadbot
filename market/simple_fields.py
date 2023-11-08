from abc import ABC
from collections import deque
from math import log

import numpy as np

from market.data_field import DataField
from shared import Bar

# High bollinger band
# Low bollinger band
# VWAP


class LogReturnField(DataField, ABC):
    def __init__(self, name: str, window_length: int):
        super().__init__(name, window_length)

        self.log_ref = deque(maxlen=window_length)
        self.data = deque(maxlen=window_length)

    def get_data(self):
        current_length = len(self.data)
        if current_length > 0:
            base = self.log_ref[0]
            log_returns = [log(x / base) for x in self.data]
        else:
            log_returns = []

        # Padding with zeros if needed
        padding_length = self.window_length - current_length
        if padding_length > 0:
            log_returns = [0.0] * padding_length + log_returns

        return np.array(log_returns)

    def add_entry(self, value: float, ref: float = 0):
        # TODO: make this log return field work
        if ref == 0:
            ref = value
        if value <= 0:
            raise ValueError("Value must be positive for log return calculation")
        self.data.append(value)
        self.log_ref.append(ref)


class OpenPriceField(LogReturnField):
    def update(self, bar: Bar):
        self.add_entry(bar.open, bar.open)


class LowPriceField(LogReturnField):
    def update(self, bar: Bar):
        self.add_entry(bar.low, bar.open)


class HighPriceField(LogReturnField):
    def update(self, bar: Bar):
        self.add_entry(bar.high, bar.open)


class ClosePriceField(LogReturnField):
    def update(self, bar: Bar):
        self.add_entry(bar.close, bar.open)


class VolumeField(LogReturnField):
    def update(self, bar: Bar):
        self.add_entry(bar.volume)


class MovingAverageField(LogReturnField):
    def __init__(self, name: str, window_length: int, period: int):
        super().__init__(name, window_length)

        self.period = period

    def update(self, bar: Bar):
        close = bar.close
        cur_len = len(self.data)

        if cur_len == 0:
            new_ma = close
        elif cur_len < self.period:
            new_ma = self.data[-1] * (cur_len / (cur_len + 1)) + close / (cur_len + 1)
        else:
            new_ma = self.data[-1] + (close - self.data[-self.period]) / self.period

        self.add_entry(new_ma)


class ExponentialMovingAverageField(LogReturnField):
    def __init__(self, name: str, window_length: int, period: int):
        super().__init__(name, window_length)

        self.period = period
        self.multiplier = 2 / (period + 1)

    def update(self, bar: Bar):
        close = bar.close
        cur_len = len(self.data)

        if cur_len == 0:
            new_ma = close
        else:
            new_ma = self.data[-1] * (1 - self.multiplier) + close * self.multiplier

        self.add_entry(new_ma)


class RSIField(DataField):
    def __init__(self, name: str, window_length: int, periods: int = 14):
        super().__init__(name, window_length)

        self.diffs = deque(maxlen=periods)
        self.prev_price = 0
        self.data = deque(maxlen=window_length)

        pass

    def get_data(self) -> np.ndarray:
        return np.array(self.data)

    def update(self, bar: Bar):
        close = bar.close

        if len(self.data) == 0:
            self.data.append(50)
            self.prev_price = close
            self.diffs.append(0)
            return

        diff = close - self.prev_price
        self.diffs.append(diff)

        self.prev_price = close

        avg_gain = sum([x for x in self.diffs if x > 0]) / len(self.diffs)
        avg_loss = abs(sum([x for x in self.diffs if x < 0])) / len(self.diffs)

        if avg_loss == 0:
            if avg_gain == 0:
                rsi = 50  # Neutral RSI when there's no gain or loss
            else:
                rsi = 100  # Max RSI when there's gain and no loss
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        self.data.append(rsi)


class MACDFIeld(DataField):
    def __init__(self, name, window_length):
        super().__init__(name, window_length)

        self.short_ema = ExponentialMovingAverageField("short_ema", window_length, 12)
        self.long_ema = ExponentialMovingAverageField("long_ema", window_length, 26)

        self.data = deque(maxlen=window_length)  # MACD value, divided by stock price

    def short_ema_price(self):
        return self.short_ema.data[-1]

    def long_ema_price(self):
        return self.long_ema.data[-1]

    def get_data(self) -> np.ndarray:
        return np.array(self.data)

    def update(self, bar: Bar):
        close = bar.close

        self.short_ema.update(bar)
        self.long_ema.update(bar)

        macd = self.short_ema_price() - self.long_ema_price()
        self.data.append(100 * macd / close)


class VWAPField(LogReturnField):
    def __init__(self, name, window_length, period: int = 60):
        super().__init__(name, window_length)

        self.period = period
        self.volumes = deque(maxlen=period)
        self.closes = deque(maxlen=period)

    def update(self, bar: Bar):
        close = bar.close
        volume = bar.volume

        self.volumes.append(volume)
        self.closes.append(close)
        current_vwap = sum([x * y for x, y in zip(self.volumes, self.closes)]) / sum(
            self.volumes
        )
        self.add_entry(current_vwap)


class HighBBField(LogReturnField):
    def __init__(self, name: str, window_length: int):
        super().__init__(name, window_length)

        self.sma = MovingAverageField("", 20, 20)
        self.std_dev = 0

    def update(self, bar: Bar):
        close = bar.close

        self.sma.update(bar)
        if len(self.data) < self.window_length:
            self.data.append(close)
            return

        std_dev = np.std(self.sma.data)
        upper_band = self.sma.data[-1] + 2 * std_dev
        self.add_entry(upper_band)


class LowBBField(LogReturnField):
    def __init__(self, name: str, window_length: int):
        super().__init__(name, window_length)

        self.sma = MovingAverageField("", 20, 20)

    def update(self, bar: Bar):
        close = bar.close

        self.sma.update(bar)
        if len(self.data) < self.window_length:
            self.data.append(close)
            return

        std_dev = np.std(self.sma.data)
        lower_band = self.sma.data[-1] - 2 * std_dev
        self.add_entry(lower_band)
