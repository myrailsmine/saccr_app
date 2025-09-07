# ui/pages/portfolio.py
"""Portfolio analysis and optimization page."""

import streamlit as st
import pandas as pd
import plotly.express as px
import json

from ai.analysis_generator import generate_portfolio_analysis


def render_portfolio_page():
    """Render the portfolio analysis page."""
    st.markdown("## Portfolio Analysis & Optimization")
    
    if 'trades_input' not in st.session_state or not st.session_state.trades_input:
        st.info("Please add trades in the SA-CCR Calculator first to perform portfolio analysis")
        return
    
    trades = st.session_state.trades_input
    
    # Portfolio overview
    _render_portfolio_overview(trades)
    
    # Portfolio composition charts
    _render_portfolio_charts(trades)
    
    # AI portfolio analysis
    _render_ai_analysis(trades)


def _render_portfolio_overview(trades):
    """Render portfolio overview metrics."""
    st.markdown("### Portfolio Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trades", len(trades))
    with col2:
        total_notional = sum(abs(t.notional) for t in trades)
        st.metric("Total Notional", f"${total_notional/1_000_000:.0f}M")
    with col3:
        asset_classes = len(set(t.asset_class for t in trades))
        st.metric("Asset Classes", asset_classes)
    with col4:
        currencies = len(set(t.currency for t in trades))
        st.metric("Currencies", currencies)


def _render_portfolio_charts(trades):
    """Render portfolio composition charts."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Notional by Asset Class")
        
        asset_class_data = {}
        for trade in trades:
            ac = trade.asset_class.value
            if ac not in asset_class_data:
                asset_class_data[ac] = 0
            asset_class_data[ac] += abs(trade.notional)
        
        ac_df = pd.DataFrame(list(asset_class_data.items()), columns=['Asset Class', 'Notional'])
        fig = px.pie(ac_df, values='Notional', names='Asset Class', 
                     title="Portfolio Composition by Asset Class")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Maturity Profile")
        
        maturity_data = []
        for trade in trades:
            maturity_data.append({
                'Trade ID': trade.trade_id,
                'Maturity (Years)': trade.time_to_maturity(),
                'Notional ($M)': abs(trade.notional) / 1_000_000
            })
        
        mat_df = pd.DataFrame(maturity_data)
        fig = px.scatter(mat_df, x='Maturity (Years)', y='Notional ($M)',
                        hover_data=['Trade ID'], title="Maturity vs Notional")
        st.plotly_chart(fig, use_container_width=True)


def _render_ai_analysis(trades):
    """Render AI portfolio analysis section."""
    if st.button("Generate AI Portfolio Analysis", type="primary"):
        with st.spinner("AI is analyzing your portfolio..."):
            
            # Prepare portfolio summary
            portfolio_summary = _prepare_portfolio_summary(trades)
            
            if hasattr(st.session_state, 'llm_client') and st.session_state.llm_client.is_connected():
                try:
                    analysis = generate_portfolio_analysis(portfolio_summary, st.session_state.llm_client)
                    st.markdown(f"""
                    <div class="ai-response">
                        <strong>AI Portfolio Analysis & Optimization Recommendations:</strong><br><br>
                        {analysis}
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"AI analysis error: {str(e)}")
            else:
                # Fallback analysis
                _render_fallback_analysis(portfolio_summary)


def _prepare_portfolio_summary(trades):
    """Prepare portfolio summary for AI analysis."""
    total_notional = sum(abs(t.notional) for t in trades)
    
    return {
        'total_trades': len(trades),
        'total_notional': total_notional,
        'asset_classes': list(set(t.asset_class.value for t in trades)),
        'currencies': list(set(t.currency for t in trades)),
        'avg_maturity': sum(t.time_to_maturity() for t in trades) / len(trades),
        'largest_trade': max(abs(t.notional) for t in trades),
        'mtm_exposure': sum(t.mtm_value for t in trades)
    }


def _render_fallback_analysis(portfolio_summary):
    """Render fallback analysis when AI is not available."""
    total_notional = portfolio_summary['total_notional']
    avg_maturity = portfolio_summary['avg_maturity']
    largest_trade = portfolio_summary['largest_trade']
    
    st.markdown(f"""
    <div class="ai-insight">
        <strong>Portfolio Analysis Summary:</strong><br><br>
        
        <strong>Portfolio Characteristics:</strong><br>
        • Total exposure: ${total_notional/1_000_000:.0f}M across {portfolio_summary['total_trades']} trades<br>
        • Asset class distribution: {', '.join(portfolio_summary['asset_classes'])}<br>
        • Currency mix: {', '.join(portfolio_summary['currencies'])}<br>
        
        <strong>Key Observations:</strong><br>
        • Average maturity: {avg_maturity:.1f} years<br>
        • Largest single trade: ${largest_trade/1_000_000:.0f}M<br>
        
        <strong>Optimization Recommendations:</strong><br>
        • Consider portfolio compression to reduce gross notional<br>
        • Evaluate netting agreement enhancements<br>
        • Assess collateral optimization opportunities<br>
        • Review concentration limits by counterparty/asset class<br>
    </div>
    """, unsafe_allow_html=True)
