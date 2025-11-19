import streamlit as st
import plotly.graph_objects as go

def render_header(current_price, price_change, pct_change):
    """
    Renders the header section with price and change.
    Args:
        current_price: Current stock price
        price_change: Absolute price change
        pct_change: Percentage change
    """
    # Determine color based on change
    change_color = "#10B981" if pct_change >= 0 else "#EF4444"
    arrow = "▲" if pct_change >= 0 else "▼"

    # Create header layout (2 columns now)
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            f"""
            <div style='padding: 20px;'>
                <h1 style='color: white; margin: 0; font-size: 48px;'>
                    ${current_price:.2f}
                </h1>
                <span style='color: {change_color}; font-size: 24px; font-weight: bold;'>
                    {arrow} {abs(pct_change):.2f}%
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style='padding: 20px;'>
                <p style='color: #94A3B8; margin: 0; font-size: 16px;'>Daily Change</p>
                <h2 style='color: white; margin: 5px 0; font-size: 36px;'>
                    {'+' if price_change >= 0 else ''}{price_change:.2f}
                </h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Moving averages indicator row (updated to match your data)
    st.markdown(
        """
        <div style='padding: 10px 20px; background: rgba(255,255,255,0.05); border-radius: 8px; margin: 10px 0;'>
            <span style='color: #06B6D4; margin-right: 20px; font-weight: bold;'>SMA(9)</span>
            <span style='color: #8B5CF6; margin-right: 20px; font-weight: bold;'>SMA(21)</span>
        </div>
        """,
        unsafe_allow_html=True,)
