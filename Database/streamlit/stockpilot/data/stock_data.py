import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import streamlit as st

class StockDataFetcher:
    """fetcher from BigQuery"""

    def __init__(self, project_id, dataset_id):
        self.project_id = project_id
        self.dataset_id = dataset_id

        # Initialize BigQuery
        if 'gcp_service_account' in st.secrets:
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
            self.client = bigquery.Client(credentials=credentials, project=project_id)
        else:
            self.client = bigquery.Client(project=project_id)

    @st.cache_data(ttl=300)
    def get_stock_data(_self, ticker, days=90):
        """stock data with basic metrics"""
        query = f"""
        SELECT
            date_time,
            open,
            high,
            low,
            close,
            volume,
            sma_21,
            sma_9,
        FROM `{_self.project_id}.{_self.dataset_id}.stocks_gold`
        WHERE ticker = '{ticker}'
        AND date_time >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY))
        ORDER BY date_time DESC
        LIMIT 60
        """

        df = _self.client.query(query).to_dataframe()
        return df.sort_values('date_time', ascending=True).reset_index(drop=True)

    @st.cache_data(ttl=350)
    def get_current_metrics(_self, ticker):
        """current price and metrics"""
        query = f"""
        SELECT
            close as current_price,
            price_change,
            ((close - LAG(close, 1) OVER (ORDER BY date_time)) / LAG(close, 1) OVER (ORDER BY date_time)) * 100 as pct_change,
            volume
        FROM `{_self.project_id}.{_self.dataset_id}.stocks_gold`
        WHERE ticker = '{ticker}'
        ORDER BY date_time DESC
        LIMIT 1
        """

        result = _self.client.query(query).to_dataframe()

        if result.empty:
            return None

        return result.iloc[0].to_dict()

    @st.cache_data(ttl=300)
    def get_volume_data(_self, ticker, periods=100):
        """volume data for chart"""
        query = f"""
        SELECT
            volume,
            AVG(volume) OVER () as avg_volume
        FROM `{_self.project_id}.{_self.dataset_id}.stocks_gold`
        WHERE ticker = '{ticker}'
        ORDER BY date_time DESC
        LIMIT {periods}
        """

        df = _self.client.query(query).to_dataframe()

        return {
            'volume_data': df['volume'].tolist()[::-1],
            'avg_volume': df['avg_volume'].iloc[0] if not df.empty else 0
        }


    @st.cache_data(ttl=300)
    def get_trend(_self, ticker):
        """trend based on moving averages"""
        query = f"""
        SELECT
            CASE
                WHEN close > sma_9 AND sma_9 > sma_21 THEN 'bullish'
                WHEN close < sma_9 AND sma_9 < sma_21 THEN 'bearish'
                ELSE 'neutral'
            END as trend
        FROM `{_self.project_id}.{_self.dataset_id}.stocks_gold`
        WHERE ticker = '{ticker}'
        ORDER BY date_time DESC
        LIMIT 1
        """

        result = _self.client.query(query).to_dataframe()

        if result.empty:
            return 'neutral'

        return result.iloc[0]['trend']

    @st.cache_data(ttl=300)
    def get_all_tickers(_self):
        """Fetch all unique tickers from BigQuery."""
        query = f"""
        SELECT DISTINCT ticker
        FROM `{_self.project_id}.{_self.dataset_id}.stocks_gold`
        ORDER BY ticker
        """
        df = _self.client.query(query).to_dataframe()

        return df["ticker"].tolist()

    @st.cache_data(ttl=300)
    def get_trading_signals(_self, ticker):
        """Generate trading signals based on technical indicators"""
        query = f"""
        WITH recent_data AS (
            SELECT
                close,
                volume,
                sma_21,
                sma_9,
                date_time,
                LAG(close, 1) OVER (ORDER BY date_time) as prev_close,
                LAG(sma_9, 1) OVER (ORDER BY date_time) as prev_sma_9,
                LAG(sma_21, 1) OVER (ORDER BY date_time) as prev_sma_21,
                LAG(close, 5) OVER (ORDER BY date_time) as close_5_ago,
                AVG(volume) OVER (ORDER BY date_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as avg_volume_20,
                MAX(close) OVER (ORDER BY date_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as high_20,
                MIN(close) OVER (ORDER BY date_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as low_20
            FROM `{_self.project_id}.{_self.dataset_id}.stocks_gold`
            WHERE ticker = '{ticker}'
            ORDER BY date_time DESC
            LIMIT 1
        ),
        latest_data AS (
            SELECT
                close,
                volume,
                sma_21,
                sma_9,
                prev_close,
                prev_sma_9,
                prev_sma_21,
                close_5_ago,
                avg_volume_20,
                high_20,
                low_20,
                CASE
                    WHEN volume > avg_volume_20 * 1.5 THEN 'high'
                    WHEN volume < avg_volume_20 * 0.5 THEN 'low'
                    ELSE 'normal'
                END as volume_signal,
                CASE
                    WHEN close > sma_9 AND sma_9 > sma_21 THEN 'bullish'
                    WHEN close < sma_9 AND sma_9 < sma_21 THEN 'bearish'
                    ELSE 'neutral'
                END as trend_signal,
                CASE
                    WHEN close >= high_20 * 0.98 THEN true
                    ELSE false
                END as near_resistance,
                CASE
                    WHEN close <= low_20 * 1.02 THEN true
                    ELSE false
                END as near_support
            FROM recent_data
        )
        SELECT
            close,
            volume,
            sma_21,
            sma_9,
            prev_close,
            prev_sma_9,
            prev_sma_21,
            close_5_ago,
            avg_volume_20,
            high_20,
            low_20,
            volume_signal,
            trend_signal,
            near_resistance,
            near_support
        FROM latest_data
        """

        result = _self.client.query(query).to_dataframe()

        if result.empty:
            return None

        return result.iloc[0].to_dict()


def load_stock_data(ticker):
    """Load all data for dashboard"""
    PROJECT_ID = st.secrets.get("gcp_project_id", "your-project-id")
    DATASET_ID = st.secrets.get("bq_dataset_id", "stock_data")

    fetcher = StockDataFetcher(PROJECT_ID, DATASET_ID)

    data = {
        'historical': fetcher.get_stock_data(ticker),
        'current': fetcher.get_current_metrics(ticker),
        'volume': fetcher.get_volume_data(ticker),
        'trend': fetcher.get_trend(ticker),
        'signals': fetcher.get_trading_signals(ticker)
    }

    return data
