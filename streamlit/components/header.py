import streamlit as st
import plotly.graph_objects as go

def render_header(current_price, price_change, pct_change, signal_score):
    """
    Renders the header section with price, change, and signal score

    Args:
        current_price: Current stock price
        price_change: Absolute price change
        pct_change: Percentage change
        signal_score: Signal score (0-100)
    """
    # Determine color based on change
    change_color = "#10b981" if pct_change >= 0 else "#ef4444"
    arrow = "▲" if pct_change >= 0 else "▼"

    # Create header layout
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        st.markdown(f"""
        <div style='padding: 20px;'>
            <h1 style='color: white; margin: 0; font-size: 48px;'>
                ${current_price:.2f}
            </h1>
            <span style='color: {change_color}; font-size: 24px; font-weight: bold;'>
                {arrow} {abs(pct_change):.2f}%
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style='padding: 20px;'>
            <p style='color: #94a3b8; margin: 0; font-size: 16px;'>Signal Score</p>
            <h2 style='color: white; margin: 5px 0; font-size: 36px;'>{signal_score:.1f}%</h2>
            <span style='color: {change_color}; font-size: 18px;'>
                {'+' if price_change >= 0 else ''}{price_change:.2f}
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        # Mini gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=signal_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
                'bar': {'color': "#10b981"},
                'bgcolor': "rgba(255,255,255,0.1)",
                'borderwidth': 2,
                'bordercolor': "#475569",
                'steps': [
                    {'range': [0, 100], 'color': 'rgba(255,255,255,0.05)'}
                ],
            }
        ))
        fig.update_layout(
            height=150,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "white", 'family': "Arial"}
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        # Moving averages indicator row
    st.markdown("""
    <div style='padding: 10px 20px; background: rgba(255,255,255,0.05); border-radius: 8px; margin: 10px 0;'>
        <span style='color: #94a3b8; margin-right: 20px;'>SMA(20)</span>
        <span style='color: #94a3b8; margin-right: 20px;'>SMA(50)</span>
        <span style='color: #f59e0b; margin-right: 20px;'>EMA</span>
        <span style='color: #94a3b8; margin-right: 20px;'>EMA(21)</span>
    </div>
    """, unsafe_allow_html=True)
