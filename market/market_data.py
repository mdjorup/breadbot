from typing import List

import numpy as np

from bar_socket import GLOBAL_BAR_SOCKET
from market.data_field import DataFieldManager


class MarketData:
    def __init__(self, window_length: int) -> None:
        self.window_length = window_length
        self.fields: List[DataFieldManager] = []

    def add_field(self, data_field_manager: DataFieldManager) -> None:
        if self.window_length == data_field_manager.window_length:
            self.fields.append(data_field_manager)
            GLOBAL_BAR_SOCKET.add_subscriber(data_field_manager)
        else:
            raise ValueError(
                f"Window length of {self.window_length} does not match {data_field_manager.window_length} for {data_field_manager.name}"
            )

    def state(self, symbol: str) -> np.ndarray:
        # go through fields, arrange the data together
        # return the data

        # here's the implementation:
        return np.concatenate([field.get_data(symbol) for field in self.fields])
