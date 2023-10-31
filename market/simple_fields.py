from abc import ABC

import numpy as np

from market.data_field import DataField
from shared import Bar


class LogReturnField(DataField, ABC):
    def __init__(self, name: str, window_length: int):
        super().__init__(name, window_length)

        self.data = np.zeros(window_length)

    def get_data(self):
        return self.data

    def add_entry(self, value: float):
        # TODO: make this log return field work
        pass


class OpenPriceField(LogReturnField):
    def update(self, bar: Bar):
        self.add_entry(bar.open)


class LowPriceField(LogReturnField):
    def update(self, bar: Bar):
        self.add_entry(bar.low)


class HighPriceField(LogReturnField):
    def update(self, bar: Bar):
        self.add_entry(bar.high)


class ClosePriceField(LogReturnField):
    def update(self, bar: Bar):
        self.add_entry(bar.close)
