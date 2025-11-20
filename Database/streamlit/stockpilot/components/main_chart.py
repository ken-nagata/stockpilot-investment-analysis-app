import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def render_main_chart(df):
    """
    Renders the main candlestick chart with moving averages and volume

    Args:
        df: DataFrame with columns: date_time, open, high, low, close, volume,
            sma_21, sma_9,
    """

    # Create subplots with candlestick and volume
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=('', '')
    )

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df['date_time'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
            increasing_line_color='#10b981',
            decreasing_line_color='#ef4444',
            increasing_fillcolor='#10b981',
            decreasing_fillcolor='#ef4444'
        ),
        row=1, col=1
    )

    # Moving Averages
    fig.add_trace(
        go.Scatter(
            x=df['date_time'],
            y=df['sma_21'],
            name='SMA(21)',
            line=dict(color='#06b6d4', width=1, dash='dot'),
            opacity=0.7
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df['date_time'],
            y=df['sma_9'],
            name='SMA(9)',
            line=dict(color='#8b5cf6', width=1, dash='dot'),
            opacity=0.7
        ),
        row=1, col=1
    )

    # fig.add_trace(
    #     go.Scatter(
    #         x=df['date_time'],
    #         y=df['ema'],
    #         name='EMA',
    #         line=dict(color='#f59e0b', width=2),
    #         opacity=0.9
    #     ),
    #     row=1, col=1
    # )

    # fig.add_trace(
    #     go.Scatter(
    #         x=df['date_time'],
    #         y=df['ema_21'],
    #         name='EMA(21)',
    #         line=dict(color='#06b6d4', width=1, dash='dash'),
    #         opacity=0.7
    #     ),
    #     row=1, col=1
    # )

    # Volume bars
    colors = ['#10b981' if close >= open else '#ef4444'
              for close, open in zip(df['close'], df['open'])]

    fig.add_trace(
        go.Bar(
            x=df['date_time'],
            y=df['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.5
        ),
        row=2, col=1
    )

    # Update layout
    fig.update_layout(
        height=600,
        plot_bgcolor='#0f172a',
        paper_bgcolor='#0f172a',
        font=dict(color='white', family='Arial', size =11),
        xaxis_rangeslider_visible=False, showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(15, 23, 42, 0.9)',
            bordercolor='#475569',
            borderwidth=2,
            font=dict(size=10, color='#e2e8f0'),
            itemsizing='constant',
            itemwidth=30
        ),
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x unified'
    )

    # Update axes
    fig.update_xaxes(
        gridcolor='#1e293b',
        showgrid=True,
        zeroline=False,
        color='#94a3b8'
    )

    fig.update_yaxes(
        gridcolor='#1e293b',
        showgrid=True,
        zeroline=False,
        color='#94a3b8',
        side='right'
    )

    # Remove rangeslider
    fig.update_xaxes(rangeslider_visible=False)

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
