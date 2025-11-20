
import streamlit as st
from data.stock_data import load_stock_data, StockDataFetcher
from components.header import render_header
from components.main_chart import render_main_chart
from components.sidebar import render_sidebar


st.set_page_config(
    page_title="STOCKPILOT",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0f172a;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Custom styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    /* Text colors - MORE SPECIFIC, exclude dropdown */
    .stApp > div > div > div > div > h1,
    .stApp > div > div > div > div > h2,
    .stApp > div > div > div > div > h3,
    .stApp > div > div > div > div > h4,
    .stApp > div > div > div > div > h5,
    .stApp > div > div > div > div > h6,
    .stApp > div > div > div > div > p {
        color: white !important;
    }
    /* Input styling */
    .stTextInput > div > div > input {
        background-color: #1e293b;
        color: white;
        border: 1px solid #475569;
    }
    /* Button styling */
    .stButton > button {
        background-color: #10b981;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stButton > button:hover {
        background-color: #059669;
    }
    /* Make dropdown options black with higher specificity */
    [data-baseweb="popover"] * {
        color: black !important;
        background-color: white !important;
    }
    ul[role="listbox"] li * {
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)
# App title
st.markdown("<h1 style='text-align: left; color: white; font-size: 48px; margin-bottom: 30px;'>STOCKPILOT</h1>",
            unsafe_allow_html=True)

# Ticker selection
col_ticker, col_refresh = st.columns([4, 1])
PROJECT_ID = st.secrets.get("gcp_project_id", "your-project-id")
DATASET_ID = st.secrets.get("bq_dataset_id", "stock_data")
fetcher = StockDataFetcher(PROJECT_ID, DATASET_ID)

with col_ticker:
    # Load tickers once using cache
    all_tickers = fetcher.get_all_tickers()

    ticker = st.selectbox(
        "Select a Stock",
        options=all_tickers,
        index=all_tickers.index("AAPL") if "AAPL" in all_tickers else 0,
        label_visibility="collapsed"
    )

with col_refresh:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
# col_ticker, col_refresh = st.columns([4, 1])
# with col_ticker:
#     ticker = st.text_input("Enter Stock Ticker", value="AAPL", label_visibility="collapsed",
#                            placeholder="Enter ticker (e.g., AAPL, GOOGL, MSFT)")
# with col_refresh:
#     if st.button("🔄 Refresh", use_container_width=True):
#         st.cache_data.clear()
#         st.rerun()

# Load data from BigQuery
try:
    with st.spinner(f"Loading data for {ticker}..."):
        data = load_stock_data(ticker)

    # Check if data is available
    if data['historical'].empty:
        st.error(f"No data found for ticker: {ticker}")
        st.stop()

    current_metrics = data['current']

    # Create main layout: left content area and right sidebar
    main_col, sidebar_col = st.columns([3, 1])

    with main_col:
        # Render header with current price
        render_header(
            current_price=current_metrics['current_price'],
            price_change=current_metrics['price_change'],
            pct_change=current_metrics['pct_change']
        )

        st.markdown("---")

        # Render main candlestick chart
        render_main_chart(data['historical'])

        # Show data info
        st.markdown("---")
        st.markdown(f"""
        <div style='padding: 10px; background: #1e293b; border-radius: 8px;'>
            <p style='color: #94a3b8; font-size: 14px; margin: 0;'>
                📊 Showing {len(data['historical'])} data points |
                Latest: {data['historical']['date_time'].max()}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with sidebar_col:
        # Render sidebar with volume and trend
        render_sidebar(
            volume_data=data['volume']['volume_data'],
            avg_volume=data['volume']['avg_volume'],
            trend=data['trend']
        )

    # Footer with last update time
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #94a3b8; font-size: 12px; padding: 20px;'>
        Last updated: {data['historical']['date_time'].max()} | Data source: BigQuery
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()
