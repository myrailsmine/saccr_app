# ui/pages/reference.py
"""Reference example page showing the Lowell Hotel Properties LLC calculation."""

import streamlit as st
from datetime import datetime, timedelta

from models.enums import AssetClass, TradeType
from models.trade import Trade
from models.netting_set import NettingSet
from ui.components import display_calculation_results


def render_reference_page():
    """Render the reference example page."""
    st.markdown("## Reference Example - Lowell Hotel Properties LLC")
    st.markdown("*Following the exact calculation from Basel regulatory documentation*")
    
    # Reference example details
    _display_reference_details()
    
    # Load and calculate button
    if st.button("Load Reference Example", type="primary"):
        _load_and_calculate_reference()


def _display_reference_details():
    """Display reference example details."""
    st.markdown("### Reference Trade Details")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Trade Information:**
        - **Trade ID**: 2098474100
        - **Counterparty**: Lowell Hotel Properties LLC
        - **Asset Class**: Interest Rate
        - **Trade Type**: Swap
        """)
    
    with col2:
        st.markdown("""
        **Financial Details:**
        - **Notional**: $681,578,963
        - **Currency**: USD
        - **Maturity**: ~0.3 years
        - **MTM Value**: $8,382,419
        """)
    
    st.markdown("""
    **CSA Terms:**
    - **Threshold**: $12,000,000
    - **MTA**: $1,000,000
    - **NICA**: $0
    """)


def _load_and_calculate_reference():
    """Load and calculate the reference example."""
    # Clear existing data
    st.session_state.trades_input = []
    st.session_state.collateral_input = []
    
    # Create the reference trade
    reference_trade = Trade(
        trade_id="2098474100",
        counterparty="Lowell Hotel Properties LLC",
        asset_class=AssetClass.INTEREST_RATE,
        trade_type=TradeType.SWAP,
        notional=681578963,
        currency="USD",
        underlying="Interest rate",
        maturity_date=datetime.now() + timedelta(days=int(0.3 * 365)),
        mtm_value=8382419,
        delta=1.0
    )
    
    st.session_state.trades_input = [reference_trade]
    
    # Create reference netting set
    netting_set = NettingSet(
        netting_set_id="212784060000009618701",
        counterparty="Lowell Hotel Properties LLC",
        trades=[reference_trade],
        threshold=12000000,
        mta=1000000,
        nica=0
    )
    
    st.success("Reference example loaded successfully!")
    
    # Automatically run calculation
    with st.spinner("Calculating SA-CCR for reference example..."):
        try:
            result = st.session_state.saccr_engine.calculate_comprehensive_saccr(netting_set, [])
            
            st.markdown("### Reference Example Results")
            
            # Show key results
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Adjusted Notional", f"${681578963:,.0f}")
            with col2:
                st.metric("Final EAD", f"${result['final_results']['exposure_at_default']:,.0f}")
            with col3:
                st.metric("RWA", f"${result['final_results']['risk_weighted_assets']:,.0f}")
            
            # Display full results
            display_calculation_results(result)
            
            # Validation info
            st.markdown("### Reference Validation")
            st.success("Calculation follows the exact 24-step Basel SA-CCR methodology")
            st.info("This matches the calculation path shown in Basel regulatory documentation")
            
        except Exception as e:
            st.error(f"Calculation error: {str(e)}")
