import json
import os
import time
from datetime import datetime, timedelta

import pytz
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.models import BarSet
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv

est = pytz.timezone("America/New_York")

stock = "SPY"

load_dotenv()

API_KEY = os.environ.get("ALPACA_KEY")
SECRET_KEY = os.environ.get("ALPACA_SECRET")


client = StockHistoricalDataClient(api_key=API_KEY, secret_key=SECRET_KEY)

start_date = datetime(2017, 1, 1)
end_date = datetime(2023, 11, 7)

cur_date = start_date

while cur_date < end_date:
    window_start = datetime(
        cur_date.year, cur_date.month, cur_date.day, 8, 30, 0, tzinfo=est
    )
    window_end = datetime(
        cur_date.year, cur_date.month, cur_date.day, 16, 0, 0, tzinfo=est
    )

    request_params = StockBarsRequest(
        symbol_or_symbols=stock,
        timeframe=TimeFrame.Minute,  # type: ignore
        start=window_start,
        end=window_end,
    )

    print(f"Getting data for date {cur_date.strftime('%Y-%m-%d')}")

    out_file_path = f"data/raw/{stock}/{cur_date.strftime('%Y-%m-%d')}.json"

    cur_date = cur_date + timedelta(days=1)

    if os.path.exists(out_file_path):
        continue

    try:
        response = client.get_stock_bars(request_params)
    except AttributeError as e:
        continue

    if not isinstance(response, BarSet):
        print("Warning: not instance of BarSet")
        continue

    data = response.data.get(stock, [])

    if len(data) == 0:
        print("Warning: No data to add")
        continue

    json_data = []

    for i, entry in enumerate(data):
        entry_json = entry.model_dump()

        new_data = {
            "i": i,
            "open": entry_json.get("open"),
            "high": entry_json.get("high"),
            "low": entry_json.get("low"),
            "close": entry_json.get("close"),
            "volume": entry_json.get("volume"),
        }

        json_data.append(new_data)

    with open(out_file_path, "w") as file:
        file.write(json.dumps(json_data))
        print("Wrote to file " + out_file_path)

    file.close()

    time.sleep(60 / 200)
