import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_indicators(df, rsi_value, macd_value, atr_value, signal_score, bb_width):
    """
    Renders technical indicators: RSI, MACD, ATR, Signal Score, and Bollinger Bands

    Args:
        df: DataFrame with date, rsi, macd, macd_signal, macd_hist, atr
        rsi_value: Current RSI value
        macd_value: Current MACD value
        atr_value: Current ATR value
        signal_score: Overall signal score
        bb_width: Bollinger Band width
    """

    # Create 3 columns for indicators
    col1, col2 = st.columns(2)

    with col1:
        # RSI Chart
        st.markdown("### RSI (14)")
        fig_rsi = go.Figure()

        fig_rsi.add_trace(go.Scatter(
            x=df['date'],
            y=df['rsi'],
            name='RSI',
            line=dict(color='white', width=2),
            fill='tozeroy',
            fillcolor='rgba(255,255,255,0.1)'
        ))

        # Add overbought/oversold lines
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="#ef4444", opacity=0.5)
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="#10b981", opacity=0.5)

        fig_rsi.update_layout(
            height=180,
            plot_bgcolor='#0f172a',
            paper_bgcolor='#1e293b',
            font=dict(color='white', size=10),
            margin=dict(l=40, r=40, t=20, b=20),
            showlegend=False,
            xaxis=dict(gridcolor='#1e293b', showgrid=True, color='#94a3b8'),
            yaxis=dict(gridcolor='#1e293b', showgrid=True, color='#94a3b8', range=[0, 100])
        )

        st.plotly_chart(fig_rsi, use_container_width=True, config={'displayModeBar': False})

        # U Inet (placeholder for custom indicator)
        st.markdown("### U Inet")
        st.markdown(f"<h3 style='color: white; text-align: right;'>3 MIN</h3>", unsafe_allow_html=True)

        # ATR Chart
        st.markdown("### ATR")
        fig_atr = go.Figure()

        fig_atr.add_trace(go.Scatter(
            x=df['date'],
            y=df['atr'],
            name='ATR',
            line=dict(color='white', width=2),
            fill='tozeroy',
            fillcolor='rgba(255,255,255,0.1)'
        ))

        fig_atr.update_layout(
            height=150,
            plot_bgcolor='#0f172a',
            paper_bgcolor='#1e293b',
            font=dict(color='white', size=10),
            margin=dict(l=40, r=40, t=20, b=20),
            showlegend=False,
            xaxis=dict(gridcolor='#1e293b', showgrid=True, color='#94a3b8'),
            yaxis=dict(gridcolor='#1e293b', showgrid=True, color='#94a3b8')
        )

        st.plotly_chart(fig_atr, use_container_width=True, config={'displayModeBar': False})

        # Signal Score display
        st.markdown("### Signal Score")
        st.markdown(f"<h2 style='color: white; text-align: right;'>{signal_score}</h2>", unsafe_allow_html=True)

    with col2:
        # MACD Chart
        st.markdown("### MACD")
        fig_macd = go.Figure()

        # MACD histogram
        colors = ['#10b981' if val >= 0 else '#ef4444' for val in df['macd_hist']]
        fig_macd.add_trace(go.Bar(
            x=df['date'],
            y=df['macd_hist'],
            name='Histogram',
            marker_color=colors,
            opacity=0.6
        ))
        # MACD and Signal lines
        fig_macd.add_trace(go.Scatter(
            x=df['date'],
            y=df['macd'],
            name='MACD',
            line=dict(color='#06b6d4', width=2)
        ))

        fig_macd.add_trace(go.Scatter(
            x=df['date'],
            y=df['macd_signal'],
            name='Signal',
            line=dict(color='#f59e0b', width=2)
        ))

        fig_macd.update_layout(
            height=180,
            plot_bgcolor='#0f172a',
            paper_bgcolor='#1e293b',
            font=dict(color='white', size=10),
            margin=dict(l=40, r=40, t=20, b=20),
            showlegend=False,
            xaxis=dict(gridcolor='#1e293b', showgrid=True, color='#94a3b8'),
            yaxis=dict(gridcolor='#1e293b', showgrid=True, color='#94a3b8')
        )

        st.plotly_chart(fig_macd, use_container_width=True, config={'displayModeBar': False})

        # MACD value display
        st.markdown(f"""
        <div style='text-align: right; padding: 10px;'>
            <span style='color: #94a3b8;'>M:0</span>
            <span style='color: white; margin-left: 20px;'>{macd_value:.3f}</span>
        </div>
        """, unsafe_allow_html=True)

        # Bollinger Band Width
        st.markdown("### Bollinger Band Width")

        # Determine sentiment
        if bb_width > 1.5:
            sentiment = "Bullish"
            sentiment_color = "#10b981"
            bar_width = min(bb_width / 2 * 100, 100)
        else:
            sentiment = "Neutral"
            sentiment_color = "#94a3b8"
            bar_width = 50

        st.markdown(f"""
        <div style='padding: 20px; background: #1e293b; border-radius: 8px;'>
            <h3 style='color: white; text-align: right;'>{bb_width:.2f}</h3>
            <div style='background: rgba(255,255,255,0.1); height: 20px; border-radius: 10px; margin: 10px 0;'>
                <div style='background: {sentiment_color}; width: {bar_width}%; height: 100%; border-radius: 10px;'></div>
            </div>
            <div style='display: flex; justify-content: space-between;'>
                <span style='color: {sentiment_color};'>{sentiment}</span>
                <span style='color: #94a3b8;'>Neutral</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
