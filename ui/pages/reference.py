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
    st.markdown("*Following the complete US SA-CCR calculation per 12 CFR 217.132*")
    
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
        - **Trade ID**: 20BN474100
        - **Counterparty**: Lowell Hotel Properties LLC
        - **Asset Class**: Interest Rate
        - **Trade Type**: Swap
        """)
    
    with col2:
        st.markdown("""
        **Financial Details:**
        - **Original Notional**: $100,000,000
        - **Currency**: USD
        - **Maturity**: ~8.33 years
        - **MTM Value**: $8,382,419
        """)
    
    st.markdown("""
    **CSA Terms:**
    - **Threshold**: $12,000,000
    - **MTA**: $1,000,000
    - **NICA**: $0
    
    **Regulatory Framework:**
    - **Regulation**: 12 CFR 217.132 (Complete Table 3 Implementation)
    - **Calculation Method**: Dual scenario (margined vs unmargined)
    - **Selection Rule**: Minimum EAD between scenarios
    """)


def _load_and_calculate_reference():
    """Load and calculate the reference example using the complete US SA-CCR engine."""
    # Clear existing data
    st.session_state.trades_input = []
    st.session_state.collateral_input = []
    
    # Create the reference trade matching the complete engine's test case
    reference_trade = Trade(
        trade_id="20BN474100",
        counterparty="Lowell Hotel Properties LLC",
        asset_class=AssetClass.INTEREST_RATE,
        trade_type=TradeType.SWAP,
        notional=100_000_000,  # $100M original notional from reference
        currency="USD",
        underlying="USD Interest Rate Swap",
        maturity_date=datetime(2029, 4, 30),  # 8.33 years maturity
        settlement_date=datetime(2020, 6, 23),  # Settlement date from reference
        mtm_value=8_382_419,  # Net MTM from reference
        delta=1.0,
        basis_flag=False,
        volatility_flag=False,
        ceu_flag=1  # CEU = 1 for reference example
    )
    
    st.session_state.trades_input = [reference_trade]
    
    # Create reference netting set
    netting_set = NettingSet(
        netting_set_id="212784060000098918701",
        counterparty="Lowell Hotel Properties LLC",
        trades=[reference_trade],
        threshold=12_000_000,   # TH = $12M from reference
        mta=1_000_000,         # MTA = $1M from reference
        nica=0                 # NICA = $0 from reference
    )
    
    st.success("Reference example loaded successfully!")
    
    # Automatically run calculation using the new dual scenario method
    with st.spinner("Calculating complete US SA-CCR per 12 CFR 217.132..."):
        try:
            # Use the new dual scenario calculation method
            result = st.session_state.saccr_engine.calculate_dual_scenario_saccr(netting_set, [])
            
            st.markdown("### Complete US SA-CCR Results (12 CFR 217.132)")
            
            # Show scenario comparison
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Margined EAD", 
                    f"${result['scenarios']['margined']['final_ead']:,.0f}",
                    help="EAD calculated under margined scenario"
                )
            with col2:
                st.metric(
                    "Unmargined EAD", 
                    f"${result['scenarios']['unmargined']['final_ead']:,.0f}",
                    help="EAD calculated under unmargined scenario"
                )
            with col3:
                st.metric(
                    "Selected EAD", 
                    f"${result['final_results']['exposure_at_default']:,.0f}",
                    help=f"Final EAD using {result['selection']['selected_scenario']} scenario"
                )
            
            # Show key regulatory details
            st.markdown("### Regulatory Compliance Details")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                **Selected Scenario:** {result['selection']['selected_scenario']}
                
                **Selection Rationale:** {result['selection']['selection_rationale']}
                
                **Key Shared Parameters:**
                - Adjusted Notional: ${result['shared_calculation_steps'][5]['total_adjusted_notional']:,.0f}
                - Supervisory Factor: {result['shared_calculation_steps'][8]['supervisory_factors'][0]['supervisory_factor_percent']:.2f}%
                - Alpha: {result['shared_calculation_steps'][20]['alpha']}
                """)
            
            with col2:
                st.markdown(f"""
                **Final Capital Requirements:**
                - Risk Weighted Assets: ${result['final_results']['risk_weighted_assets']:,.0f}
                - Capital Requirement: ${result['final_results']['capital_requirement']:,.0f}
                
                **Regulatory Reference:**
                - {result['regulatory_reference']}
                - Table 3 Implementation: {result['table_3_implementation']}
                """)
            
            # Display comprehensive results
            st.markdown("### Detailed Calculation Results")
            display_calculation_results(result)
            
            # Validation against expected values
            st.markdown("### Reference Validation")
            
            # Expected values from the complete engine's validation
            expected_final_ead = 11_790_314
            calculated_ead = result['final_results']['exposure_at_default']
            variance_pct = abs((calculated_ead - expected_final_ead) / expected_final_ead) * 100
            
            if variance_pct <= 2.0:  # Within 2% tolerance
                st.success(f"✅ Validation PASSED: Calculated EAD ${calculated_ead:,.0f} matches expected ${expected_final_ead:,.0f} (variance: {variance_pct:.1f}%)")
            else:
                st.warning(f"⚠️ Validation check: Calculated EAD ${calculated_ead:,.0f} vs expected ${expected_final_ead:,.0f} (variance: {variance_pct:.1f}%)")
            
            st.info("This calculation follows the complete 24-step Basel SA-CCR methodology with full US regulatory compliance per 12 CFR 217.132")
            
        except Exception as e:
            st.error(f"Calculation error: {str(e)}")
            st.markdown("**Debug Information:**")
            st.write(f"Error type: {type(e).__name__}")
            st.write(f"Available engine methods: {[method for method in dir(st.session_state.saccr_engine) if not method.startswith('_')]}")
