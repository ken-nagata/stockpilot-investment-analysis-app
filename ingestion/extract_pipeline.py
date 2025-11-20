#!/usr/bin/env python

# ---------------------------------------------------------
# Upload ticker parquet files to GCS
# This script:
#   1) Fetches minute/daily stock data from yfinance
#   2) Normalizes + enriches metadata
#   3) Writes 1 parquet file *per ticker per run*
#   4) Uploads files to:
#         gs://daily_stock_tickers/raw/<DATE>/<TICKER>_<TS>.parquet


import pandas as pd
import yfinance as yf
from google.cloud import storage
from datetime import datetime, UTC
from zoneinfo import ZoneInfo
from pathlib import Path
import logging
import os
import pyarrow as pa
import pyarrow.parquet as pq
import gcsfs



BUCKET_NAME = os.getenv("BUCKET_NAME")

# ---------------------------------------------------------
# 1. FETCH EQUITY DATA
# ---------------------------------------------------------
def fetch_equity(tickers, period_, interval_):
    frames = []

    for ticker in tickers:
        print(f"[INFO] Pulling data for {ticker}…")

        data = yf.download(
            ticker,
            period=period_,
            interval=interval_,
            auto_adjust=False,
            progress=False,
        )

        if data.empty:
            print(f"[WARN] No data for {ticker}, skipping.")
            continue

        # Remove MultiIndex if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            data.columns.name = None

        # Normalize columns
        data = data.reset_index().rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adj_close",
                "Volume": "volume",
            }
        )


        if "adj_close" not in data.columns and "close" in data.columns:
            data["adj_close"] = data["close"]

        # Metadata (resilient)
        t = yf.Ticker(ticker)
        currency = "UNKNOWN"
        name = ticker

        try:
            fast = t.fast_info or {}
            currency = fast.get("currency") or "UNKNOWN"
        except Exception:
            pass

        try:
            info = t.get_info()
            name = info.get("longName") or info.get("shortName") or ticker
        except Exception:
            pass

        # Add identifiers + timezone conversions
        data["ticker"] = ticker
        data["currency"] = currency
        data["name"] = name
        data["source"] = "yfinance"
        data["date"] = pd.to_datetime(data["Datetime"]).dt.date
        # Convert to tz-naive UTC (drop timezone)
        data["ingested_at"] = datetime.now(UTC)
        data["date_time"] = (pd.to_datetime(data["Datetime"], utc=True).dt.tz_localize(None).astype("datetime64[us]"))
        # Datetime is not necessary anymore
        data = data.drop(columns=["Datetime"])

        # Final order of the selected/created columns
        cols = [
            "date_time",
            "ticker",
            "name",
            "currency",
            "open",
            "high",
            "low",
            "close",
            "adj_close",
            "volume",
            "source",
            "date",
            "ingested_at",
        ]

        data = data[cols].dropna(subset=["close"])
        frames.append(data)

    if not frames:
        return pd.DataFrame(columns=cols)

    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------
# 2. GENERATE GCS PATH FOR EACH FILE
# ---------------------------------------------------------
def make_gcs_path(symbol: str, batch_ts: datetime) -> str:
    date_str = batch_ts.date().isoformat()                 # "2025-11-18"
    ts_str = batch_ts.strftime("%Y-%m-%dT%H-%M-%SZ")       # "2025-11-18T20-11-00Z"
    return f"raw/{date_str}/{symbol}_{ts_str}.parquet"

# ---------------------------------------------------------
# 3. WRITE TO PARQUET
# ---------------------------------------------------------

def write_parquet_to_gcs(df: pd.DataFrame, gcs_path: str):
    fs = gcsfs.GCSFileSystem()  # uses ADC credentials
    df = df.reset_index(drop=True)
    table = pa.Table.from_pandas(df, preserve_index=False)

    full_uri = f"gs://{BUCKET_NAME}/{gcs_path}"

    with fs.open(full_uri, "wb") as f:
        pq.write_table(table, f)

    return full_uri

# ---------------------------------------------------------
# 4. MAIN FUNCTION FOR AIRFLOW
# ---------------------------------------------------------
def run_ingestion(
    tickers,
    period_="1d",
    interval_="1m",
    **context,
):
    """
    Main entry point for Airflow.
    Fetches data for given tickers, writes 1 parquet per ticker to GCS.
    """
    if not BUCKET_NAME:
        raise RuntimeError("BUCKET_NAME env var is not set")

    print(f"[INFO] Fetching tickers = {tickers} / period={period_} / interval={interval_}")

    batch_ts = datetime.now(UTC)
    df = fetch_equity(tickers, period_, interval_)

    if df.empty:
        print("[WARN] No data fetched. Exiting.")
        return []

    uris = []

    for symbol in df["ticker"].unique():
        df_sym = df[df["ticker"] == symbol].copy()
        print(f"[INFO] Writing parquet for {symbol} ({len(df_sym)} rows)")
        gcs_path = make_gcs_path(symbol, batch_ts)
        uri = write_parquet_to_gcs(df_sym, gcs_path)
        print(f"[SUCCESS] Uploaded {symbol} → {uri}")
        uris.append(uri)

    return uris


# ---------------------------------------------------------
# 5. LOCAL TEST ENTRYPOINT
# ---------------------------------------------------------
if __name__ == "__main__":
    tickers = ["LEU"]
    run_ingestion(tickers=tickers, period_="1d", interval_="1m")
