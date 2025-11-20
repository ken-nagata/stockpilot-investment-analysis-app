import streamlit as st
import plotly.graph_objects as go

def render_sidebar(volume_data, avg_volume, trend):
    """
    Renders the right sidebar with volume and trend
    Args:
        volume_data: List of recent volume values
        avg_volume: Average volume
        trend: Trend direction ('bullish', 'bearish', 'neutral')
    """
    # Volume Section
    st.markdown("<h2 style='color: white;'>Volume</h2>", unsafe_allow_html=True)

    # Volume bar chart
    fig_volume = go.Figure()
    colors = ['#10B981' if v > avg_volume else '#475569' for v in volume_data]

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
        line_color="#94A3B8",
        opacity=0.5,
        annotation_text=f"Avg: {avg_volume/1e6:.1f}M",
        annotation_position="right"
    )

    fig_volume.update_layout(
        height=200,
        plot_bgcolor='#0F172A',
        paper_bgcolor='#1E293B',
        font=dict(color='white', size=10),
        margin=dict(l=40, r=40, t=20, b=40),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(gridcolor='#1E293B', showgrid=True, color='#94A3B8')
    )

    st.plotly_chart(fig_volume, use_container_width=True, config={'displayModeBar': False})

    # Display current volume
    current_volume = volume_data[-1] if volume_data else 0
    st.markdown(f"""
    <div style='text-align: center; padding: 10px;'>
        <h3 style='color: white; margin: 0;'>{current_volume/1e6:.1f}M</h3>
        <p style='color: #94A3B8; margin: 0; font-size: 12px;'>Avg: {avg_volume/1e6:.1f}M</p>
    </div>
    """, unsafe_allow_html=True)

    # Alerts Section


    # Trend Section
    st.markdown("<h2 style='color: white;'>Trend</h2>", unsafe_allow_html=True)

    if trend == 'bullish':
        trend_color = "#10B981"
        bar_width = 80
        trend_label = "Bullish"
    elif trend == 'bearish':
        trend_color = "#EF4444"
        bar_width = 20
        trend_label = "Bearish"
    else:
        trend_color = "#94A3B8"
        bar_width = 50
        trend_label = "Neutral"

    st.markdown(f"""
    <div style='padding: 20px; background: #1E293B; border-radius: 8px;'>
        <div style='background: rgba(255,255,255,0.1); height: 20px; border-radius: 10px; margin: 10px 0;'>
            <div style='background: {trend_color}; width: {bar_width}%; height: 100%; border-radius: 10px;'></div>
        </div>
        <div style='text-align: center; margin-top: 10px;'>
            <span style='color: {trend_color}; font-size: 18px; font-weight: bold;'>{trend_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
