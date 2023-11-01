from abc import ABC
from collections import deque
from math import log

import numpy as np

from market.data_field import DataField
from shared import Bar


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


class RSI(DataField):
    def get_data(self) -> np.ndarray:
        return np.array([])

    def update(self):
        pass
