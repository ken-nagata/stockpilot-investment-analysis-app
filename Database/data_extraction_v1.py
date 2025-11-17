import pandas as pd
import yfinance as yf
import logging
import os


# Input from team
tickers = ["NVDA","AAPL"]
period="1d"
interval="5m"
parquet_file="wei_stock_10m_test.parquet"


logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
log = logging.getLogger(__name__)

# Create a function to fetch stocks information based on input
def fetch_equity(tickers,period,interval):
    frames = []

    for ticker in tickers:
        # 1) Download prices or skip
        data = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False)
        if data is None or data.empty:
            log.warning(f"[warn] {ticker}: no data returned; skipping")
            continue
        # 2) Remove yfinance MultiIndex
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            data.columns.name = None

        # 3) Fetch metadata and add to table
        ticker_info = yf.Ticker(ticker)
        currency = ticker_info.fast_info["currency"] or ticker_info.get_info()["currency"] or "UNKNOWN"
        name = ticker_info.get_info()["longName"] or ticker_info.get_info()["shortName"] or ticker
        data["currency"] = currency
        data["name"] = name
        data["datetime"]=pd.Timestamp.now(tz="UTC")

        frames.append(data)

    out = pd.concat(frames, ignore_index=True)
    return out


# Write data to parquet file
def update_parquet(df_new):
    if os.path.exists(parquet_file):
        print("loading exisiting file...")
        df_old=pd.read_parquet(parquet_file)
        df=pd.concat([df_old,df_new])
    else:
        df=df_new

    df.to_parquet(parquet_file,index=False)


# Call function examples
df_new=fetch_equity(tickers,period,interval)
update_parquet(df_new)
