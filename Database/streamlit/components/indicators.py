import streamlit as st
import plotly.graph_objects as go

def render_indicators(df, rsi_value, signal_score):
    """
    Renders RSI indicator (simplified version)

    Args:
        df: DataFrame with date and rsi
        rsi_value: Current RSI value
        signal_score: Overall signal score
    """

    # Single column layout for simplified view
    st.markdown("---")
    st.markdown("## Technical Indicators")

    col1, col2 = st.columns([2, 1])

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
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="#ef4444", opacity=0.5,
                          annotation_text="Overbought")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="#10b981", opacity=0.5,
                          annotation_text="Oversold")
        fig_rsi.add_hline(y=50, line_dash="dot", line_color="#94a3b8", opacity=0.3)

        fig_rsi.update_layout(
            height=300,
            plot_bgcolor='#0f172a',
            paper_bgcolor='#1e293b',
            font=dict(color='white', size=12),
            margin=dict(l=50, r=50, t=30, b=30),
            showlegend=False,
            xaxis=dict(gridcolor='#1e293b', showgrid=True, color='#94a3b8'),
            yaxis=dict(gridcolor='#1e293b', showgrid=True, color='#94a3b8', range=[0, 100])
        )

        st.plotly_chart(fig_rsi, use_container_width=True, config={'displayModeBar': False})

        # RSI value display
        rsi_color = "#ef4444" if rsi_value > 70 else "#10b981" if rsi_value < 30 else "#94a3b8"
        rsi_status = "Overbought" if rsi_value > 70 else "Oversold" if rsi_value < 30 else "Neutral"

        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: #1e293b; border-radius: 8px; margin-top: 10px;'>
            <h2 style='color: {rsi_color}; margin: 0;'>{rsi_value:.2f}</h2>
            <p style='color: #94a3b8; margin: 5px 0 0 0;'>{rsi_status}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Signal Score display
        st.markdown("### Signal Score")

        # Determine color based on score
        if signal_score >= 70:
            score_color = "#10b981"
            score_text = "Strong"
        elif signal_score >= 40:
            score_color = "#f59e0b"
            score_text = "Moderate"
        else:
            score_color = "#ef4444"
            score_text = "Weak"

        st.markdown(f"""
        <div style='text-align: center; padding: 30px; background: #1e293b; border-radius: 8px;'>
            <h1 style='color: {score_color}; margin: 0; font-size: 72px;'>{signal_score:.0f}</h1>
            <p style='color: #94a3b8; margin: 10px 0 0 0; font-size: 18px;'>{score_text}</p>
        </div>
        """, unsafe_allow_html=True)

        # Simple interpretation guide
        st.markdown("""
        <div style='margin-top: 20px; padding: 15px; background: #1e293b; border-radius: 8px;'>
            <p style='color: #94a3b8; font-size: 12px; margin: 5px 0;'>
                <span style='color: #10b981;'>● 70-100:</span> Strong signal<br>
                <span style='color: #f59e0b;'>● 40-69:</span> Moderate signal<br>
                <span style='color: #ef4444;'>● 0-39:</span> Weak signal
            </p>
        </div>
        """, unsafe_allow_html=True)
