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
            date,
            open,
            high,
            low,
            close,
            volume,
            sma_20,
            sma_50,
            ema,
            rsi,
            signal_score
        FROM `{_self.project_id}.{_self.dataset_id}.stock_metrics`
        WHERE ticker = '{ticker}'
        AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
        ORDER BY date ASC
        """

        df = _self.client.query(query).to_dataframe()
        return df

    @st.cache_data(ttl=60)
    def get_current_metrics(_self, ticker):
        """current price and metrics"""
        query = f"""
        SELECT
            close as current_price,
            close - LAG(close, 1) OVER (ORDER BY date) as price_change,
            ((close - LAG(close, 1) OVER (ORDER BY date)) / LAG(close, 1) OVER (ORDER BY date)) * 100 as pct_change,
            signal_score,
            rsi,
            volume
        FROM `{_self.project_id}.{_self.dataset_id}.stock_metrics`
        WHERE ticker = '{ticker}'
        ORDER BY date DESC
        LIMIT 1
        """

        result = _self.client.query(query).to_dataframe()

        if result.empty:
            return None

        return result.iloc[0].to_dict()

    @st.cache_data(ttl=300)
    def get_volume_data(_self, ticker, periods=20):
        """volume data for chart"""
        query = f"""
        SELECT
            volume,
            AVG(volume) OVER () as avg_volume
        FROM `{_self.project_id}.{_self.dataset_id}.stock_metrics`
        WHERE ticker = '{ticker}'
        ORDER BY date DESC
        LIMIT {periods}
        """

        df = _self.client.query(query).to_dataframe()

        return {
            'volume_data': df['volume'].tolist()[::-1],
            'avg_volume': df['avg_volume'].iloc[0] if not df.empty else 0
        }

    @st.cache_data(ttl=300)
    def get_alerts(_self, ticker):
        """simple alerts"""
        metrics = _self.get_current_metrics(ticker)
        alerts = []

        if metrics:
            # RSI alerts
            if metrics.get('rsi', 50) > 70:
                alerts.append({'message': 'RSI above 70', 'active': True})
            elif metrics.get('rsi', 50) < 30:
                alerts.append({'message': 'RSI below 30', 'active': True})

            # Volume alerts
            volume_data = _self.get_volume_data(ticker)
            if volume_data['volume_data'][-1] > volume_data['avg_volume'] * 1.5:
                alerts.append({'message': 'Volume spike', 'active': True})

        # Default message if no alerts
        if not alerts:
            alerts.append({'message': 'No alerts', 'active': False})

        return alerts

    @st.cache_data(ttl=300)
    def get_trend(_self, ticker):
        """trend based on moving averages"""
        query = f"""
        SELECT
            CASE
                WHEN close > sma_20 AND sma_20 > sma_50 THEN 'bullish'
                WHEN close < sma_20 AND sma_20 < sma_50 THEN 'bearish'
                ELSE 'neutral'
            END as trend
        FROM `{_self.project_id}.{_self.dataset_id}.stock_metrics`
        WHERE ticker = '{ticker}'
        ORDER BY date DESC
        LIMIT 1
        """

        result = _self.client.query(query).to_dataframe()

        if result.empty:
            return 'neutral'

        return result.iloc[0]['trend']


def load_stock_data(ticker):
    """Load all data for dashboard"""
    PROJECT_ID = st.secrets.get("gcp_project_id", "your-project-id")
    DATASET_ID = st.secrets.get("bq_dataset_id", "stock_data")

    fetcher = StockDataFetcher(PROJECT_ID, DATASET_ID)

    data = {
        'historical': fetcher.get_stock_data(ticker),
        'current': fetcher.get_current_metrics(ticker),
        'volume': fetcher.get_volume_data(ticker),
        'alerts': fetcher.get_alerts(ticker),
        'trend': fetcher.get_trend(ticker)
    }

    return data
