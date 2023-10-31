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

    def add_entry(self, value: float, ref: float):
        # TODO: make this log return field work
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
        self.add_entry(bar.volume, bar.volume)


class MovingAverageField(LogReturnField):
    def __init__(self, name: str, window_length: int, period: int):
        super().__init__(name, window_length)
        self.data = deque(maxlen=window_length)
