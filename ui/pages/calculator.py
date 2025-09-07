# ui/pages/calculator.py
"""Main SA-CCR calculator page with trade input and calculation display."""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import List

from models.enums import AssetClass, TradeType, CollateralType
from models.trade import Trade
from models.netting_set import NettingSet
from models.collateral import Collateral
from config.settings import MAJOR_CURRENCIES
from ui.components import display_calculation_results
from utils.data_export import export_calculation_results


def render_calculator_page():
    """Render the main SA-CCR calculator page."""
    st.markdown("## SA-CCR Calculator")
    st.markdown("*Following the complete 24-step Basel regulatory framework*")
    
    # Step 1: Netting Set Configuration
    with st.expander("Step 1: Netting Set Configuration", expanded=True):
        netting_set_config = _render_netting_set_config()
    
    # Step 2: Trade Portfolio Input
    st.markdown("### Trade Portfolio Input")
    trades = _render_trade_input()
    
    # Step 3: Collateral Input
    collateral = _render_collateral_input()
    
    # Validation and Calculation
    if st.button("Calculate Complete SA-CCR", type="primary"):
        _execute_calculation(netting_set_config, trades, collateral)


def _render_netting_set_config():
    """Render netting set configuration section."""
    col1, col2 = st.columns(2)
    
    with col1:
        netting_set_id = st.text_input(
            "Netting Set ID*", 
            placeholder="e.g., 212784060000009618701",
            help="Unique identifier for the netting set"
        )
        counterparty = st.text_input(
            "Counterparty*", 
            placeholder="e.g., Lowell Hotel Properties LLC",
            help="Legal name of the counterparty"
        )
        
    with col2:
        threshold = st.number_input(
            "Threshold ($)*", 
            min_value=0.0, 
            value=1000000.0, 
            step=100000.0,
            help="Credit Support Annex threshold amount"
        )
        mta = st.number_input(
            "MTA ($)*", 
            min_value=0.0, 
            value=500000.0, 
            step=50000.0,
            help="Minimum Transfer Amount"
        )
        nica = st.number_input(
            "NICA ($)", 
            min_value=0.0, 
            value=0.0, 
            step=10000.0,
            help="Net Independent Collateral Amount"
        )
    
    return {
        'netting_set_id': netting_set_id,
        'counterparty': counterparty,
        'threshold': threshold,
        'mta': mta,
        'nica': nica
    }


def _render_trade_input():
    """Render trade input section."""
    if 'trades_input' not in st.session_state:
        st.session_state.trades_input = []
    
    with st.expander("Add New Trade", expanded=len(st.session_state.trades_input) == 0):
        trade_form = _render_trade_form()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add Trade", type="primary"):
                if _validate_trade_form(trade_form):
                    new_trade = _create_trade_from_form(trade_form)
                    st.session_state.trades_input.append(new_trade)
                    st.success(f"Added trade {trade_form['trade_id']}")
                    st.rerun()
                else:
                    st.error("Please fill all required fields marked with *")
        
        with col2:
            if st.button("Clear All Trades"):
                st.session_state.trades_input = []
                st.rerun()
    
    # Display current trades
    if st.session_state.trades_input:
        _display_current_trades()
    
    return st.session_state.trades_input


def _render_trade_form():
    """Render the trade input form."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        trade_id = st.text_input("Trade ID*", placeholder="e.g., 2098474100")
        asset_class = st.selectbox("Asset Class*", [ac.value for ac in AssetClass])
        trade_type = st.selectbox("Trade Type*", [tt.value for tt in TradeType])
    
    with col2:
        notional = st.number_input("Notional ($)*", min_value=0.0, value=100000000.0, step=1000000.0)
        currency = st.selectbox("Currency*", MAJOR_CURRENCIES)
        underlying = st.text_input("Underlying*", placeholder="e.g., Interest rate")
    
    with col3:
        maturity_years = st.number_input("Maturity (Years)*", min_value=0.1, max_value=30.0, value=5.0, step=0.1)
        mtm_value = st.number_input("MTM Value ($)", value=0.0, step=10000.0)
        delta = st.number_input("Delta (for options)", min_value=-1.0, max_value=1.0, value=1.0, step=0.1)
    
    return {
        'trade_id': trade_id,
        'asset_class': asset_class,
        'trade_type': trade_type,
        'notional': notional,
        'currency': currency,
        'underlying': underlying,
        'maturity_years': maturity_years,
        'mtm_value': mtm_value,
        'delta': delta
    }


def _validate_trade_form(trade_form):
    """Validate trade form inputs."""
    required_fields = ['trade_id', 'notional', 'currency', 'underlying']
    return all(trade_form.get(field) for field in required_fields) and trade_form['notional'] > 0


def _create_trade_from_form(trade_form):
    """Create Trade object from form data."""
    return Trade(
        trade_id=trade_form['trade_id'],
        counterparty="",  # Will be set from netting set
        asset_class=AssetClass(trade_form['asset_class']),
        trade_type=TradeType(trade_form['trade_type']),
        notional=trade_form['notional'],
        currency=trade_form['currency'],
        underlying=trade_form['underlying'],
        maturity_date=datetime.now() + timedelta(days=int(trade_form['maturity_years'] * 365)),
        mtm_value=trade_form['mtm_value'],
        delta=trade_form['delta']
    )


def _display_current_trades():
    """Display current trade portfolio."""
    st.markdown("### Current Trade Portfolio")
    
    trades_data = []
    for i, trade in enumerate(st.session_state.trades_input):
        trades_data.append({
            'Index': i,
            'Trade ID': trade.trade_id,
            'Asset Class': trade.asset_class.value,
            'Type': trade.trade_type.value,
            'Notional ($M)': f"{trade.notional/1_000_000:.1f}",
            'Currency': trade.currency,
            'MTM ($K)': f"{trade.mtm_value/1000:.0f}",
            'Maturity (Y)': f"{trade.time_to_maturity():.1f}"
        })
    
    df = pd.DataFrame(trades_data)
    st.dataframe(df, use_container_width=True)
    
    # Remove trade option
    if len(st.session_state.trades_input) > 0:
        remove_idx = st.selectbox("Remove trade by index:", [-1] + list(range(len(st.session_state.trades_input))))
        if remove_idx >= 0 and st.button("Remove Selected Trade"):
            st.session_state.trades_input.pop(remove_idx)
            st.rerun()


def _render_collateral_input():
    """Render collateral input section."""
    if 'collateral_input' not in st.session_state:
        st.session_state.collateral_input = []
    
    with st.expander("Collateral Portfolio", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            coll_type = st.selectbox("Collateral Type", [ct.value for ct in CollateralType])
        with col2:
            coll_currency = st.selectbox("Collateral Currency", MAJOR_CURRENCIES)
        with col3:
            coll_amount = st.number_input("Amount ($)", min_value=0.0, value=10000000.0, step=1000000.0)
        
        if st.button("Add Collateral"):
            new_collateral = Collateral(
                collateral_type=CollateralType(coll_type),
                currency=coll_currency,
                amount=coll_amount
            )
            st.session_state.collateral_input.append(new_collateral)
            st.success(f"Added {coll_type} collateral")
        
        if st.session_state.collateral_input:
            st.markdown("**Current Collateral:**")
            for i, coll in enumerate(st.session_state.collateral_input):
                st.write(f"{i+1}. {coll.collateral_type.value}: ${coll.amount:,.0f} {coll.currency}")
    
    return st.session_state.collateral_input


def _execute_calculation(netting_set_config, trades, collateral):
    """Execute SA-CCR calculation."""
    # Validate inputs
    if not netting_set_config['netting_set_id'] or not netting_set_config['counterparty'] or not trades:
        st.error("Please provide Netting Set ID, Counterparty, and at least one trade")
        return
    
    # Create netting set
    netting_set = NettingSet(
        netting_set_id=netting_set_config['netting_set_id'],
        counterparty=netting_set_config['counterparty'],
        trades=trades,
        threshold=netting_set_config['threshold'],
        mta=netting_set_config['mta'],
        nica=netting_set_config['nica']
    )
    
    # Update trade counterparty
    for trade in netting_set.trades:
        trade.counterparty = netting_set.counterparty
    
    # Validate completeness
    validation = st.session_state.saccr_engine.validate_input_completeness(netting_set, collateral)
    
    if not validation['is_complete']:
        st.error("Missing required information:")
        for field in validation['missing_fields']:
            st.write(f"   • {field}")
        st.markdown("### Please provide missing information and try again.")
        return
    
    if validation['warnings']:
        st.warning("Warnings (calculation will proceed with defaults):")
        for warning in validation['warnings']:
            st.write(f"   • {warning}")
    
    # Perform calculation
    with st.spinner("Performing complete 24-step SA-CCR calculation..."):
        try:
            result = st.session_state.saccr_engine.calculate_comprehensive_saccr(netting_set, collateral)
            display_calculation_results(result)
        except Exception as e:
            st.error(f"Calculation error: {str(e)}")
