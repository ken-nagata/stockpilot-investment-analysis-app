import streamlit.components as st
import plotly.graph_objects as go

def render_sidebar(signal_score, volume_data, avg_volume, alerts, trend):
    """
    Renders the right sidebar with signal score, volume, alerts, and trend

    Args:
        signal_score: Overall signal score (0-100)
        volume_data: List of recent volume values
        avg_volume: Average volume
        alerts: List of alert dictionaries with 'message' and 'active' keys
        trend: Trend direction ('bullish', 'bearish', 'neutral')
    """

    st.markdown("## Signal Score")

    # Large circular gauge
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=signal_score,
        number={'font': {'size': 60, 'color': 'white'}},
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Neutral", 'font': {'size': 20, 'color': '#94a3b8'}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 0, 'tickcolor': "white"},
            'bar': {'color': "#10b981", 'thickness': 0.25},
            'bgcolor': "rgba(255,255,255,0.05)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 100], 'color': 'rgba(255,255,255,0.05)'}
            ],
            'threshold': {
                'line': {'color': "#10b981", 'width': 4},
                'thickness': 0.75,
                'value': signal_score
            }
        }
    ))

    fig_gauge.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "white", 'family': "Arial"}
    )

    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

    # Volume Section
    st.markdown("## Volume")

    # Volume bar chart
    fig_volume = go.Figure()

    colors = ['#10b981' if v > avg_volume else '#475569' for v in volume_data]

    fig_volume.add_trace(go.Bar(
        y=volume_data,
        marker_color=colors,
        width=0.8,
        showlegend=False
    ))

    # Add average line
    fig_volume.add_hline(
        y=avg_volume,
        line_dash="dash",
        line_color="#94a3b8",
        opacity=0.5,
        annotation_text=f"Avg: {avg_volume/1e6:.1f}M",
        annotation_position="right"
    )

    fig_volume.update_layout(
        height=200,
        plot_bgcolor='#0f172a',
        paper_bgcolor='#1e293b',
        font=dict(color='white', size=10),
        margin=dict(l=40, r=40, t=20, b=40),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(gridcolor='#1e293b', showgrid=True, color='#94a3b8')
    )

    st.plotly_chart(fig_volume, use_container_width=True, config={'displayModeBar': False})

    # Display current volume
    current_volume = volume_data[-1] if volume_data else 0
    st.markdown(f"""
    <div style='text-align: center; padding: 10px;'>
        <h3 style='color: white; margin: 0;'>{current_volume/1e6:.1f}M</h3>
        <p style='color: #94a3b8; margin: 0; font-size: 12px;'>Avg: {avg_volume/1e6:.1f}M</p>
    </div>
    """, unsafe_allow_html=True)

    # Alerts Section
    st.markdown("## Alerts")

    for alert in alerts:
        indicator_color = "#10b981" if alert.get('active', False) else "#475569"
        st.markdown(f"""
        <div style='padding: 12px; background: #1e293b; border-radius: 8px; margin-bottom: 10px;
                    border-left: 4px solid {indicator_color};'>
            <div style='display: flex; align-items: center;'>
                <div style='width: 12px; height: 12px; background: {indicator_color};
                            border-radius: 50%; margin-right: 12px;'></div>
                <span style='color: white; font-size: 14px;'>{alert['message']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Trend Section
    st.markdown("## Trend")

    # Determine trend color and width
    if trend == 'bullish':
        trend_color = "#10b981"
        bar_width = 80
        trend_label = "Bullish"
    elif trend == 'bearish':
        trend_color = "#ef4444"
        bar_width = 20
        trend_label = "Bearish"
    else:
        trend_color = "#94a3b8"
        bar_width = 50
        trend_label = "Neutral"

    st.markdown(f"""
    <div style='padding: 20px; background: #1e293b; border-radius: 8px;'>
        <div style='background: rgba(255,255,255,0.1); height: 20px; border-radius: 10px; margin: 10px 0;'>
            <div style='background: {trend_color}; width: {bar_width}%; height: 100%; border-radius: 10px;'></div>
        </div>
        <div style='text-align: center; margin-top: 10px;'>
            <span style='color: {trend_color}; font-size: 18px; font-weight: bold;'>{trend_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
