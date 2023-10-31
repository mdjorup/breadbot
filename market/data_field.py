from abc import ABC, abstractmethod
from typing import Dict, Type

import numpy as np

from shared import Bar
from sockets.bar_socket import BarSubscriber


class DataField(ABC):
    def __init__(self, name, window_length):
        self.name = name
        self.window_length = window_length

    @abstractmethod
    def get_data(self) -> np.ndarray:
        pass

    @abstractmethod
    def update(self, bar: Bar) -> None:
        pass


class DataFieldManager(BarSubscriber):
    def __init__(
        self, field_name: str, window_length: int, data_field_class: Type[DataField]
    ):
        self.window_length = window_length
        self.name = field_name
        self.data_field_class = data_field_class
        self.data_fields: Dict[
            str, data_field_class
        ] = {}  # maps a symbol to a datafield

    def __check_symbol(self, symbol: str):
        assert symbol in self.data_fields, f"Symbol {symbol} not in {self.name}"

    def register_symbol(self, symbol: str):
        if symbol not in self.data_fields:
            self.data_fields[symbol] = self.data_field_class(
                self.name, self.window_length
            )
        else:
            raise ValueError(f"Symbol {symbol} is already registered in {self.name}")

    def update_bar(self, bar: Bar):
        symbol = bar.symbol
        self.__check_symbol(symbol)
        self.data_fields[symbol].update(bar)

    def get_data(self, symbol) -> np.ndarray:
        self.__check_symbol(symbol)
        return self.data_fields[symbol].get_data()
