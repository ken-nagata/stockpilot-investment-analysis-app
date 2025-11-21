import streamlit as st

def render_alerts(signals):
    """
    Renders trading alerts based on technical indicators
    Args:
        signals: Dictionary with trading signal data
    """
    if signals is None:
        st.warning("Unable to generate trading signals")
        return

    # Analyze signals and generate recommendation
    buy_score = 0
    sell_score = 0
    alerts = []

    # Volume Analysis
    if signals['volume_signal'] == 'high':
        if signals['trend_signal'] == 'bullish':
            buy_score += 1
            alerts.append({
                'type': 'bullish',
                'title': '📈 High Volume + Bullish',
                'message': 'Volume surge during uptrend - Strong buying interest'
            })
        elif signals['trend_signal'] == 'bearish':
            sell_score += 1
            alerts.append({
                'type': 'bearish',
                'title': '📉 High Volume + Bearish',
                'message': 'Volume surge during downtrend - Strong selling pressure'
            })
    elif signals['volume_signal'] == 'low':
        alerts.append({
            'type': 'neutral',
            'title': '📊 Low Volume',
            'message': 'Volume 50% below average - Weak market interest'
        })

    # Trend Analysis
    if signals['trend_signal'] == 'bullish':
        buy_score += 2
        alerts.append({
            'type': 'bullish',
            'title': '🚀 Bullish Trend',
            'message': 'Price above both SMAs - Uptrend confirmed'
        })
    elif signals['trend_signal'] == 'bearish':
        sell_score += 2
        alerts.append({
            'type': 'bearish',
            'title': '⚠️ Bearish Trend',
            'message': 'Price below both SMAs - Downtrend confirmed'
        })
    else:
        alerts.append({
            'type': 'neutral',
            'title': '➖ Neutral Trend',
            'message': 'Mixed signals - No clear trend'
        })

    # Golden Cross / Death Cross
    if signals['sma_9'] > signals['sma_21'] and signals['prev_sma_9'] <= signals['prev_sma_21']:
        buy_score += 3
        alerts.append({
            'type': 'bullish',
            'title': '✨ Golden Cross Alert',
            'message': 'SMA(9) crossed above SMA(21) - Strong buy signal!'
        })
    elif signals['sma_9'] < signals['sma_21'] and signals['prev_sma_9'] >= signals['prev_sma_21']:
        sell_score += 3
        alerts.append({
            'type': 'bearish',
            'title': '💀 Death Cross Alert',
            'message': 'SMA(9) crossed below SMA(21) - Strong sell signal!'
        })

    # Price momentum (short-term)
    price_change_pct = ((signals['close'] - signals['prev_close']) / signals['prev_close']) * 100
    if price_change_pct > 3:
        buy_score += 1
        alerts.append({
            'type': 'bullish',
            'title': '⬆️ Strong Momentum',
            'message': f'Price up {price_change_pct:.2f}% - Positive momentum'
        })
    elif price_change_pct < -3:
        sell_score += 1
        alerts.append({
            'type': 'bearish',
            'title': '⬇️ Negative Momentum',
            'message': f'Price down {abs(price_change_pct):.2f}% - Selling pressure'
        })

    # Medium-term price trend (5 periods)
    if signals['close_5_ago'] is not None:
        medium_change_pct = ((signals['close'] - signals['close_5_ago']) / signals['close_5_ago']) * 100
        if medium_change_pct < -5:
            sell_score += 1
            alerts.append({
                'type': 'bearish',
                'title': '📉 Declining Trend',
                'message': f'Price down {abs(medium_change_pct):.2f}% over recent periods'
            })
        elif medium_change_pct > 5:
            buy_score += 1
            alerts.append({
                'type': 'bullish',
                'title': '📈 Rising Trend',
                'message': f'Price up {medium_change_pct:.2f}% over recent periods'
            })

    # Resistance level check (potential sell zone)
    if signals.get('near_resistance', False):
        sell_score += 1
        alerts.append({
            'type': 'bearish',
            'title': '🚧 Near Resistance',
            'message': f'Price near 20-period high (${signals["high_20"]:.2f}) - Consider taking profits'
        })

    # Support level check (potential buy zone)
    if signals.get('near_support', False):
        buy_score += 1
        alerts.append({
            'type': 'bullish',
            'title': '🛡️ Near Support',
            'message': f'Price near 20-period low (${signals["low_20"]:.2f}) - Potential buy opportunity'
        })

    # Price breaking below SMA(21) - Strong sell signal
    if signals['close'] < signals['sma_21'] and signals['prev_close'] >= signals['prev_sma_21']:
        sell_score += 2
        alerts.append({
            'type': 'bearish',
            'title': '🔻 Breaking Support',
            'message': 'Price broke below SMA(21) - Consider selling'
        })

    # Price breaking above SMA(21) - Strong buy signal
    if signals['close'] > signals['sma_21'] and signals['prev_close'] <= signals['prev_sma_21']:
        buy_score += 2
        alerts.append({
            'type': 'bullish',
            'title': '🔺 Breaking Resistance',
            'message': 'Price broke above SMA(21) - Consider buying'
        })

    # Calculate net score
    net_score = buy_score - sell_score

    # Generate overall recommendation
    if net_score >= 4:
        recommendation = {
            'action': 'STRONG BUY',
            'color': '#10B981',
            'icon': '🟢',
            'message': 'Multiple strong buy signals detected',
            'score_display': f'Buy: {buy_score} | Sell: {sell_score}'
        }
    elif net_score >= 2:
        recommendation = {
            'action': 'BUY',
            'color': '#3B82F6',
            'icon': '🔵',
            'message': 'Moderate buy signals present',
            'score_display': f'Buy: {buy_score} | Sell: {sell_score}'
        }
    elif net_score <= -4:
        recommendation = {
            'action': 'STRONG SELL',
            'color': '#DC2626',
            'icon': '🔴',
            'message': 'Multiple strong sell signals detected',
            'score_display': f'Buy: {buy_score} | Sell: {sell_score}'
        }
    elif net_score <= -2:
        recommendation = {
            'action': 'SELL',
            'color': '#F59E0B',
            'icon': '🟠',
            'message': 'Moderate sell signals present',
            'score_display': f'Buy: {buy_score} | Sell: {sell_score}'
        }
    else:
        recommendation = {
            'action': 'HOLD',
            'color': '#94A3B8',
            'icon': '⚪',
            'message': 'Mixed signals - Hold current position',
            'score_display': f'Buy: {buy_score} | Sell: {sell_score}'
        }

    # Render recommendation box
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, {recommendation['color']}22 0%, {recommendation['color']}11 100%);
                    border-left: 4px solid {recommendation['color']};
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;'>
            <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                <span style='font-size: 32px; margin-right: 15px;'>{recommendation['icon']}</span>
                <div>
                    <h2 style='color: {recommendation['color']}; margin: 0; font-size: 28px;'>{recommendation['action']}</h2>
                    <p style='color: #94A3B8; margin: 5px 0 0 0; font-size: 14px;'>{recommendation['message']}</p>
                </div>
            </div>
            <p style='color: #64748B; font-size: 12px; margin: 10px 0 0 0;'>
                {recommendation['score_display']} | Net Score: {net_score}
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Render individual alerts
    st.markdown("<h3 style='color: white; margin-top: 20px;'>Active Signals</h3>", unsafe_allow_html=True)

    for alert in alerts:
        if alert['type'] == 'bullish':
            bg_color = '#10B98122'
            border_color = '#10B981'
        elif alert['type'] == 'bearish':
            bg_color = '#EF444422'
            border_color = '#EF4444'
        else:
            bg_color = '#94A3B822'
            border_color = '#94A3B8'

        st.markdown(f"""
            <div style='background: {bg_color};
                        border-left: 3px solid {border_color};
                        border-radius: 6px;
                        padding: 15px;
                        margin-bottom: 10px;'>
                <h4 style='color: white; margin: 0 0 5px 0; font-size: 16px;'>{alert['title']}</h4>
                <p style='color: #94A3B8; margin: 0; font-size: 14px;'>{alert['message']}</p>
            </div>
        """, unsafe_allow_html=True)

    # Disclaimer
    st.markdown("""
        <div style='background: #1E293B; border-radius: 6px; padding: 15px; margin-top: 20px;'>
            <p style='color: #64748B; font-size: 12px; margin: 0;'>
                ⚠️ <strong>Disclaimer:</strong> These signals are generated from technical analysis and should not be considered financial advice.
                Always do your own research and consult with a financial advisor before making investment decisions.
            </p>
        </div>
    """, unsafe_allow_html=True)
