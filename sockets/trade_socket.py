import os
import threading
from abc import ABC, abstractmethod

from alpaca.trading.stream import TradingStream
from dotenv import load_dotenv

from shared import Trade


class TradeSubscriber(ABC):
    @abstractmethod
    def update_trade(self, trade: Trade):
        pass


class TradeSocket:
    def __init__(self):
        load_dotenv()
        self.stream = TradingStream(
            os.environ.get("ALPACA_KEY", ""),
            os.environ.get("ALPACA_SECRET", ""),
            paper=True,
        )

        self.stop_flag = threading.Event()
        self.subscribers: list[TradeSubscriber] = []

    def add_subscriber(self, subscriber):
        self.subscribers.append(subscriber)

    async def update_all(self, data):
        if not data.qty or not data.price:
            return

        side = data.order.side
        symbol = data.order.symbol
        qty = float(data.qty)
        price = float(data.price)
        timestamp = data.timestamp

        trade = Trade(side, symbol, qty, price, timestamp)

        for sub in self.subscribers:
            sub.update_trade(trade)

    def run(self):
        # Create and start the thread
        self.thread = threading.Thread(target=self._run_thread)
        self.thread.start()
        self.stream.subscribe_trade_updates(self.update_all)
        print("Trade socket running in a separate thread")

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


GLOBAL_TRADE_SOCKET = TradeSocket()
