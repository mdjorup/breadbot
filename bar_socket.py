import os
import threading
from abc import ABC, abstractmethod

from alpaca.data.live import StockDataStream
from dotenv import load_dotenv

from shared import Bar


class BarSubscriber(ABC):
    @abstractmethod
    def update_bar(self, bar: Bar):
        pass


class BarSocket:
    def __init__(self) -> None:
        load_dotenv()

        self.stream = StockDataStream(
            os.environ.get("ALPACA_KEY", ""), os.environ.get("ALPACA_SECRET", "")
        )

        self.stop_flag = threading.Event()
        self.subscribers: list[BarSubscriber] = []

        self.active_subs = set()

    def add_subscriber(self, subscriber):
        self.subscribers.append(subscriber)

    async def update_all(self, data):
        # convert data into a bar

        symbol = data.symbol
        opn = float(data.open)
        high = float(data.high)
        low = float(data.low)
        close = float(data.close)
        volume = float(data.volume)
        timestamp = data.timestamp

        bar = Bar(symbol, opn, high, low, close, volume, timestamp)

        for sub in self.subscribers:
            sub.update_bar(bar)

    def subscribe_to_symbol(self, symbol):
        if symbol in self.active_subs:
            return
        self.stream.subscribe_bars(self.update_all, symbol)
        self.active_subs.add(symbol)

    def unsubscribe_from_symbol(self, symbol):
        if not symbol in self.active_subs:
            return
        self.stream.unsubscribe_bars(symbol)
        self.active_subs.remove(symbol)

    def run(self):
        self.thread = threading.Thread(target=self._run_thread)
        self.thread.start()

    def _run_thread(self):
        # Run the stream until the stop flag is set
        try:
            self.stream.run()  # Assuming this is a blocking call
        except Exception as e:
            print("Error in stream: ", e)

    def stop(self):
        # Signal the thread to stop and wait for it to finish
        self.stop_flag.set()
        self.stream.stop()
        self.thread.join()


GLOBAL_BAR_SOCKET = BarSocket()
