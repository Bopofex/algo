import pandas as pd
import requests
from pathlib import Path
import time


# =========================
# Configuration
# =========================

SYMBOL = "BTCUSDT"
INTERVAL = "15m"

BASE_URL = "https://api.binance.com/api/v3/klines"

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = DATA_DIR / f"{SYMBOL}_{INTERVAL}.csv"


# =========================
# Download Binance Data
# =========================

def download_klines(symbol, interval, start_time=None, end_time=None):
    all_data = []

    current_start = start_time

    while True:
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": 1000
        }

        if current_start is not None:
            params["startTime"] = current_start

        if end_time is not None:
            params["endTime"] = end_time

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if not data:
            break

        all_data.extend(data)

        last_open_time = data[-1][0]

        if len(data) < 1000:
            break

        current_start = last_open_time + 1

        time.sleep(0.2)

    return all_data


# =========================
# Convert to DataFrame
# =========================

def convert_to_dataframe(data):

    columns = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_volume",
        "number_of_trades",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
        "ignore"
    ]

    df = pd.DataFrame(data, columns=columns)

    df["open_time"] = pd.to_datetime(
        df["open_time"],
        unit="ms",
        utc=True
    )

    df["close_time"] = pd.to_datetime(
        df["close_time"],
        unit="ms",
        utc=True
    )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_volume"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df[
        [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time"
        ]
    ]

    return df


# =========================
# Main
# =========================

if __name__ == "__main__":

    print(f"Downloading {SYMBOL} {INTERVAL} data...")

    data = download_klines(
        symbol=SYMBOL,
        interval=INTERVAL
    )

    df = convert_to_dataframe(data)

    df = df.drop_duplicates(
        subset=["open_time"]
    )

    df = df.sort_values(
        "open_time"
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print(f"Rows downloaded: {len(df):,}")
    print(f"First candle: {df['open_time'].min()}")
    print(f"Last candle:  {df['open_time'].max()}")
    print(f"Saved to: {OUTPUT_FILE}")
