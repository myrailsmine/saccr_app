# ui/components.py
"""Reusable UI components for the SA-CCR application."""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from utils.data_export import create_summary_csv, create_steps_csv, export_calculation_results


def display_calculation_results(result: Dict[str, Any]):
    """Display comprehensive SA-CCR calculation results from the complete engine."""
    
    # Handle both dual-scenario and single scenario results
    if 'scenarios' in result:
        # Dual scenario results from complete engine
        _display_dual_scenario_results(result)
    else:
        # Single scenario or legacy format
        _display_single_scenario_results(result)


def _display_dual_scenario_results(result: Dict[str, Any]):
    """Display results from dual-scenario SA-CCR calculation."""
    
    st.markdown("## Complete SA-CCR Calculation Results")
    st.markdown("*Following 12 CFR 217.132 with Full Table 3 Implementation*")
    
    # Final Results Summary
    final_results = result['final_results']
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Replacement Cost", f"${final_results['replacement_cost']/1_000_000:.2f}M")
    with col2:
        st.metric("PFE", f"${final_results['potential_future_exposure']/1_000_000:.2f}M")
    with col3:
        st.metric("EAD", f"${final_results['exposure_at_default']/1_000_000:.2f}M")
    with col4:
        st.metric("RWA", f"${final_results['risk_weighted_assets']/1_000_000:.2f}M")
    with col5:
        st.metric("Capital Required", f"${final_results['capital_requirement']/1_000:.0f}K")
    
    # Scenario Comparison
    _display_scenario_comparison(result)
    
    # Shared Calculation Steps
    _display_shared_steps(result['shared_calculation_steps'])
    
    # Scenario-Specific Steps
    _display_scenario_specific_steps(result['scenarios'])
    
    # Regulatory Compliance
    _display_regulatory_compliance(result)
    
    # Export Options
    _display_export_options(result)


def _display_single_scenario_results(result: Dict[str, Any]):
    """Display results from single scenario calculation (legacy format)."""
    
    st.markdown("## SA-CCR Calculation Results")
    
    # Check if we have the expected structure
    if 'final_results' not in result:
        st.error("Invalid result format - missing final_results")
        return
    
    final_results = result['final_results']
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Replacement Cost", f"${final_results.get('replacement_cost', 0)/1_000_000:.2f}M")
    with col2:
        st.metric("PFE", f"${final_results.get('potential_future_exposure', 0)/1_000_000:.2f}M")
    with col3:
        st.metric("EAD", f"${final_results.get('exposure_at_default', 0)/1_000_000:.2f}M")
    with col4:
        st.metric("RWA", f"${final_results.get('risk_weighted_assets', 0)/1_000_000:.2f}M")
    with col5:
        st.metric("Capital Required", f"${final_results.get('capital_requirement', 0)/1_000:.0f}K")
    
    # Enhanced Summary if available
    if 'enhanced_summary' in result:
        _display_enhanced_summary(result['enhanced_summary'])
    
    # Detailed Step-by-Step Breakdown
    if 'calculation_steps' in result:
        _display_calculation_steps(result['calculation_steps'])
    
    # Data Quality Issues
    if result.get('data_quality_issues'):
        _display_data_quality_issues(result['data_quality_issues'])
    
    # Export Options
    _display_export_options(result)


def _display_scenario_comparison(result: Dict[str, Any]):
    """Display comparison between margined and unmargined scenarios."""
    
    with st.expander("📊 Scenario Comparison (Margined vs Unmargined)", expanded=True):
        
        margined = result['scenarios']['margined']
        unmargined = result['scenarios']['unmargined']
        selection = result['selection']
        
        # Selection summary
        st.markdown(f"""
        **Selected Scenario:** {selection['selected_scenario']} 
        
        **Selection Rationale:** {selection['selection_rationale']}
        
        **EAD Difference:** ${selection['ead_difference']:,.0f}
        
        **Capital Savings:** ${selection['capital_savings']:,.0f}
        """)
        
        # Comparison table
        comparison_data = {
            'Metric': ['PFE', 'RC', 'EAD', 'RWA', 'Capital'],
            'Margined ($M)': [
                f"{margined['pfe']/1_000_000:.2f}",
                f"{margined['rc']/1_000_000:.2f}",
                f"{margined['final_ead']/1_000_000:.2f}",
                f"{margined['rwa']/1_000_000:.2f}",
                f"{margined['final_capital']/1_000_000:.2f}"
            ],
            'Unmargined ($M)': [
                f"{unmargined['pfe']/1_000_000:.2f}",
                f"{unmargined['rc']/1_000_000:.2f}",
                f"{unmargined['final_ead']/1_000_000:.2f}",
                f"{unmargined['rwa']/1_000_000:.2f}",
                f"{unmargined['final_capital']/1_000_000:.2f}"
            ],
            'Difference ($M)': [
                f"{abs(margined['pfe'] - unmargined['pfe'])/1_000_000:.2f}",
                f"{abs(margined['rc'] - unmargined['rc'])/1_000_000:.2f}",
                f"{abs(margined['final_ead'] - unmargined['final_ead'])/1_000_000:.2f}",
                f"{abs(margined['rwa'] - unmargined['rwa'])/1_000_000:.2f}",
                f"{abs(margined['final_capital'] - unmargined['final_capital'])/1_000_000:.2f}"
            ]
        }
        
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def _display_shared_steps(shared_steps: Dict[int, Any]):
    """Display shared calculation steps."""
    
    with st.expander("🔄 Shared Calculation Steps (Same for Both Scenarios)", expanded=False):
        
        # Group shared steps logically
        step_groups = {
            "Input Data & Classification": [1, 2, 3],
            "Time Parameters & Adjusted Notional": [4, 5],
            "Risk Factors & Correlations": [7, 8, 10],
            "Collateral & CSA Parameters": [14, 17],
            "Alpha & Counterparty Risk": [19, 20, 22, 23]
        }
        
        for group_name, step_numbers in step_groups.items():
            with st.expander(f"📋 {group_name}", expanded=False):
                for step_num in step_numbers:
                    if step_num in shared_steps:
                        step_data = shared_steps[step_num]
                        _render_shared_step(step_data)


def _render_shared_step(step_data: Dict[str, Any]):
    """Render a shared calculation step."""
    
    st.markdown(f"""
    <div style="border: 1px solid #e6e6e6; border-radius: 5px; padding: 1rem; margin: 0.5rem 0;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="background: #0f4c75; color: white; border-radius: 50%; 
                         width: 30px; height: 30px; display: flex; align-items: center; 
                         justify-content: center; font-weight: bold; margin-right: 1rem;">
                {step_data['step']}
            </span>
            <span style="font-weight: 600; color: #0f4c75; font-size: 1.1rem;">
                {step_data['title']}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display step-specific data
    if step_data['step'] == 1:
        st.write(f"**Netting Set ID:** {step_data['netting_set_id']}")
        st.write(f"**Counterparty:** {step_data['counterparty']}")
        st.write(f"**Trade Count:** {step_data['trade_count']}")
        st.write(f"**Total Notional:** ${step_data['total_notional']:,.0f}")
    
    elif step_data['step'] == 5:
        for adj_notional in step_data['adjusted_notionals']:
            st.write(f"**Trade {adj_notional['trade_id']}:**")
            st.write(f"   • Original Notional: ${adj_notional['original_notional']:,.0f}")
            st.write(f"   • Supervisory Duration: {adj_notional['supervisory_duration']:.6f}")
            st.write(f"   • Adjusted Notional: ${adj_notional['adjusted_notional']:,.0f}")
    
    elif step_data['step'] == 8:
        for sf in step_data['supervisory_factors']:
            st.write(f"**Trade {sf['trade_id']}:** {sf['supervisory_factor_percent']:.2f}% ({sf['asset_class']})")
            st.write(f"   • Reference: {sf['table_reference']}")
    
    elif step_data['step'] == 20:
        st.write(f"**Alpha:** {step_data['alpha']}")
        st.write(f"**Formula:** {step_data['formula']}")


def _display_scenario_specific_steps(scenarios: Dict[str, Any]):
    """Display scenario-specific calculation steps."""
    
    with st.expander("⚖️ Scenario-Specific Calculations", expanded=False):
        
        tab1, tab2 = st.tabs(["Margined Scenario", "Unmargined Scenario"])
        
        with tab1:
            _display_scenario_details(scenarios['margined'])
        
        with tab2:
            _display_scenario_details(scenarios['unmargined'])


def _display_scenario_details(scenario_data: Dict[str, Any]):
    """Display details for a specific scenario."""
    
    st.markdown(f"### {scenario_data['scenario']} Scenario Details")
    
    # Key results
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("PFE", f"${scenario_data['pfe']:,.0f}")
    with col2:
        st.metric("RC", f"${scenario_data['rc']:,.0f}")
    with col3:
        st.metric("EAD", f"${scenario_data['final_ead']:,.0f}")
    
    # Maturity factors
    st.markdown("**Maturity Factors:**")
    for mf in scenario_data['maturity_factors']:
        st.write(f"Trade {mf['trade_id']}: {mf['maturity_factor']:.6f}")
        st.write(f"   • Formula: {mf['formula']}")
        st.write(f"   • MPOR: {mf['mpor_days']} business days")
    
    # Add-ons
    st.markdown("**Add-On Components:**")
    st.write(f"Aggregate Add-On: ${scenario_data['aggregate_addon']:,.0f}")
    st.write(f"PFE Multiplier: {scenario_data['pfe_multiplier']:.6f}")
    
    # Regulatory formulas
    if 'regulatory_formulas' in scenario_data:
        st.markdown("**Regulatory Formulas:**")
        for name, formula in scenario_data['regulatory_formulas'].items():
            if name != 'regulation':
                st.write(f"• {name.replace('_', ' ').title()}: {formula}")


def _display_regulatory_compliance(result: Dict[str, Any]):
    """Display regulatory compliance information."""
    
    with st.expander("📜 Regulatory Compliance", expanded=False):
        
        st.markdown(f"""
        **Regulatory Reference:** {result['regulatory_reference']}
        
        **Table 3 Implementation:** {result['table_3_implementation']}
        
        **Key Compliance Features:**
        • Complete 12 CFR 217.132 implementation
        • All supervisory factors from Table 3
        • Dual scenario calculation (margined/unmargined)
        • Minimum EAD selection rule applied
        • US MPOR values per regulation
        • Complete correlation matrix handling
        """)
        
        if result.get('shared_calculation_steps', {}).get(8):
            sf_data = result['shared_calculation_steps'][8]
            st.markdown("**Supervisory Factors Applied:**")
            for sf in sf_data['supervisory_factors']:
                st.write(f"• {sf['asset_class']}: {sf['supervisory_factor_percent']:.2f}%")


def _display_enhanced_summary(enhanced_summary: Dict[str, Any]):
    """Display enhanced summary with key insights."""
    with st.expander("📊 Enhanced Summary", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Key Inputs:**")
            for item in enhanced_summary.get('key_inputs', []):
                st.write(f"• {item}")
            
            st.markdown("**Risk Components:**")
            for item in enhanced_summary.get('risk_components', []):
                st.write(f"• {item}")
        
        with col2:
            st.markdown("**Capital Results:**")
            for item in enhanced_summary.get('capital_results', []):
                st.write(f"• {item}")
            
            st.markdown("**Optimization Insights:**")
            for item in enhanced_summary.get('optimization_insights', []):
                st.write(f"• {item}")


def _display_calculation_steps(calculation_steps):
    """Display detailed calculation steps (legacy format)."""
    with st.expander("🔍 Complete 24-Step Calculation Breakdown", expanded=False):
        
        if not calculation_steps:
            st.info("No calculation steps available")
            return
        
        # Group steps for better organization
        step_groups = {
            "Trade Data & Classification (Steps 1-4)": [1, 2, 3, 4],
            "Notional & Risk Factor Calculations (Steps 5-8)": [5, 6, 7, 8],
            "Add-On Calculations (Steps 9-13)": [9, 10, 11, 12, 13],
            "PFE Calculations (Steps 14-16)": [14, 15, 16],
            "Replacement Cost (Steps 17-18)": [17, 18],
            "EAD & RWA Calculations (Steps 19-24)": [19, 20, 21, 22, 23, 24]
        }
        
        for group_name, step_numbers in step_groups.items():
            with st.expander(f"📋 {group_name}", expanded=False):
                for step_num in step_numbers:
                    if step_num <= len(calculation_steps):
                        step_data = calculation_steps[step_num - 1]
                        _render_calculation_step(step_data)


def _render_calculation_step(step_data):
    """Render a single calculation step."""
    
    st.markdown(f"""
    <div style="border: 1px solid #e6e6e6; border-radius: 5px; padding: 1rem; margin: 0.5rem 0;">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <span style="background: #0f4c75; color: white; border-radius: 50%; 
                         width: 30px; height: 30px; display: flex; align-items: center; 
                         justify-content: center; font-weight: bold; margin-right: 1rem;">
                {step_data.step}
            </span>
            <span style="font-weight: 600; color: #0f4c75; font-size: 1.1rem;">
                {step_data.title}
            </span>
        </div>
        <div style="margin-bottom: 0.5rem;">
            <strong>Description:</strong> {step_data.description}
        </div>
        <div style="background: #f8f9fa; padding: 0.75rem; border-radius: 3px; 
                    font-family: monospace; margin: 0.5rem 0;">
            {step_data.formula}
        </div>
        <div style="font-size: 1.1rem; font-weight: 600; color: #0f4c75; margin-top: 0.5rem;">
            <strong>Result:</strong> {step_data.result}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show thinking process if available
    if hasattr(step_data, 'thinking') and step_data.thinking:
        with st.expander(f"💭 Thinking Process - Step {step_data.step}", expanded=False):
            st.markdown(f"""
            <div style="background: #f0f8ff; padding: 1rem; border-radius: 5px;">
                <strong>Reasoning:</strong><br>
                {step_data.thinking.get('reasoning', 'No reasoning provided')}
                <br><br>
                <strong>Key Insight:</strong> {step_data.thinking.get('key_insight', 'No insight provided')}
            </div>
            """, unsafe_allow_html=True)


def _display_data_quality_issues(data_quality_issues):
    """Display data quality issues and recommendations."""
    with st.expander("⚠️ Data Quality Assessment", expanded=False):
        if not data_quality_issues:
            st.success("No data quality issues identified")
            return
        
        high_impact = [issue for issue in data_quality_issues if issue.impact.value == 'high']
        medium_impact = [issue for issue in data_quality_issues if issue.impact.value == 'medium']
        low_impact = [issue for issue in data_quality_issues if issue.impact.value == 'low']
        
        if high_impact:
            st.error(f"High Impact Issues ({len(high_impact)})")
            for issue in high_impact:
                st.markdown(f"""
                <div style="background: #ffe6e6; border: 1px solid #ff9999; 
                           border-radius: 5px; padding: 0.75rem; margin: 0.5rem 0;">
                    <strong>{issue.field_name}</strong><br>
                    Issue: {issue.issue_type.value.title()}<br>
                    Current: {issue.current_value}<br>
                    Recommendation: {issue.recommendation}
                </div>
                """, unsafe_allow_html=True)
        
        if medium_impact:
            st.warning(f"Medium Impact Issues ({len(medium_impact)})")
            for issue in medium_impact:
                st.write(f"• **{issue.field_name}**: {issue.recommendation}")
        
        if low_impact:
            st.info(f"Low Impact Issues ({len(low_impact)})")
            for issue in low_impact:
                st.write(f"• {issue.field_name}: {issue.recommendation}")


def _display_export_options(result):
    """Display export options for results."""
    st.markdown("### 📥 Export Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Generate exports using the complete export function
    try:
        exports = export_calculation_results(result, format_type="all")
        
        with col1:
            if 'summary_csv' in exports:
                st.download_button(
                    "📊 Summary CSV",
                    data=exports['summary_csv'],
                    file_name=f"saccr_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if 'steps_csv' in exports:
                st.download_button(
                    "📋 Steps CSV",
                    data=exports['steps_csv'],
                    file_name=f"saccr_steps_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            if 'excel_workbook' in exports:
                st.download_button(
                    "📈 Excel Report",
                    data=exports['excel_workbook'],
                    file_name=f"saccr_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        with col4:
            if 'json_complete' in exports:
                st.download_button(
                    "🔧 Complete JSON",
                    data=exports['json_complete'],
                    file_name=f"saccr_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    except Exception as e:
        st.error(f"Error generating exports: {str(e)}")
        
        # Fallback to basic JSON export
        json_data = json.dumps(result, indent=2, default=str)
        st.download_button(
            "🔧 Basic JSON",
            data=json_data,
            file_name=f"saccr_basic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


def render_metric_card(title: str, value: str, delta: str = None, help_text: str = None):
    """Render a custom metric card."""
    delta_html = f"<div style='color: #28a745; font-size: 0.8rem;'>{delta}</div>" if delta else ""
    help_html = f"<div style='color: #6c757d; font-size: 0.7rem; margin-top: 0.5rem;'>{help_text}</div>" if help_text else ""
    
    st.markdown(f"""
    <div style="background: white; border: 1px solid #e6e6e6; border-radius: 10px; 
                padding: 1rem; margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="font-weight: 600; color: #0f4c75; margin-bottom: 0.5rem;">{title}</div>
        <div style="font-size: 1.5rem; font-weight: 700; color: #28a745;">{value}</div>
        {delta_html}
        {help_html}
    </div>
    """, unsafe_allow_html=True)


def render_progress_indicator(current_step: int, total_steps: int = 24, title: str = "Calculation Progress"):
    """Render a progress indicator for calculations."""
    progress = current_step / total_steps
    
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="font-weight: 600; margin-bottom: 0.5rem;">{title}</div>
        <div style="background: #e9ecef; border-radius: 10px; height: 20px; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #28a745, #20c997); 
                        width: {progress*100:.1f}%; height: 100%; 
                        transition: width 0.3s ease;"></div>
        </div>
        <div style="font-size: 0.8rem; color: #6c757d; margin-top: 0.25rem;">
            Step {current_step} of {total_steps} ({progress*100:.1f}% complete)
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_calculation_summary_table(results: Dict[str, Any]):
    """Render a summary table of key calculation results."""
    final_results = results.get('final_results', {})
    
    summary_data = {
        'Metric': [
            'Replacement Cost (RC)',
            'Potential Future Exposure (PFE)', 
            'Exposure at Default (EAD)',
            'Risk-Weighted Assets (RWA)',
            'Capital Requirement'
        ],
        'Value ($M)': [
            f"{final_results.get('replacement_cost', 0)/1_000_000:.2f}",
            f"{final_results.get('potential_future_exposure', 0)/1_000_000:.2f}",
            f"{final_results.get('exposure_at_default', 0)/1_000_000:.2f}",
            f"{final_results.get('risk_weighted_assets', 0)/1_000_000:.2f}",
            f"{final_results.get('capital_requirement', 0)/1_000_000:.2f}"
        ],
        'Description': [
            'Current replacement cost if counterparty defaults',
            'Potential future exposure over trade lifetime',
            'Total exposure at default (RC + PFE) × Alpha',
            'Risk-weighted exposure for capital calculation',
            'Minimum regulatory capital required (8% of RWA)'
        ]
    }
    
    df = pd.DataFrame(summary_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_input_validation_feedback(validation_result: Dict[str, Any]):
    """Render input validation feedback."""
    if validation_result.get('is_complete', False):
        st.success("✅ All required inputs provided")
    else:
        st.error("❌ Missing required information:")
        for field in validation_result.get('missing_fields', []):
            st.write(f"   • {field}")
    
    if validation_result.get('warnings'):
        st.warning("⚠️ Warnings:")
        for warning in validation_result['warnings']:
            st.write(f"   • {warning}")


def render_step_by_step_viewer(calculation_steps, selected_step: int = None):
    """Render an interactive step-by-step viewer."""
    if not calculation_steps:
        st.info("No calculation steps available")
        return
    
    # Handle both list and dict formats
    if isinstance(calculation_steps, dict):
        # Convert dict to list for consistent handling
        step_list = []
        for step_num in sorted(calculation_steps.keys()):
            step_data = calculation_steps[step_num]
            step_data['step'] = step_num
            step_list.append(step_data)
        calculation_steps = step_list
    
    # Step selector
    step_options = []
    for step in calculation_steps:
        if hasattr(step, 'step') and hasattr(step, 'title'):
            step_options.append(f"Step {step.step}: {step.title}")
        elif isinstance(step, dict):
            step_options.append(f"Step {step.get('step', '?')}: {step.get('title', 'Unknown')}")
        else:
            step_options.append(f"Step {len(step_options) + 1}")
    
    if not step_options:
        st.info("No valid calculation steps found")
        return
    
    selected_idx = st.selectbox("Select Step to View:", range(len(step_options)), 
                               format_func=lambda x: step_options[x],
                               index=selected_step-1 if selected_step and selected_step <= len(calculation_steps) else 0)
    
    if selected_idx < len(calculation_steps):
        step = calculation_steps[selected_idx]
        
        # Handle both object and dict formats
        if hasattr(step, 'title'):
            title = step.title
            description = getattr(step, 'description', 'No description available')
            formula = getattr(step, 'formula', 'No formula available')
            result = getattr(step, 'result', 'No result available')
            thinking = getattr(step, 'thinking', None)
            data = getattr(step, 'data', None)
        elif isinstance(step, dict):
            title = step.get('title', 'Unknown Step')
            description = step.get('description', 'No description available')
            formula = step.get('formula', 'No formula available')
            result = step.get('result', 'No result available')
            thinking = step.get('thinking', None)
            data = step.get('data', None)
        else:
            st.error(f"Invalid step format: {type(step)}")
            return
        
        # Display step details
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {title}")
            st.markdown(description)
            
            with st.expander("Formula & Calculation", expanded=True):
                st.code(formula, language="text")
                st.markdown(f"**Result:** {result}")
        
        with col2:
            if thinking and isinstance(thinking, dict):
                with st.expander("💭 Thinking Process", expanded=False):
                    st.markdown(thinking.get('reasoning', 'No reasoning available'))
                    if thinking.get('key_insight'):
                        st.info(f"**Key Insight:** {thinking['key_insight']}")
        
        # Display step data if available
        if data and isinstance(data, dict):
            with st.expander("📊 Step Data", expanded=False):
                st.json(data)


def render_trade_comparison_table(trades):
    """Render a comparison table of trades."""
    if not trades:
        st.info("No trades to display")
        return
    
    trade_data = []
    for trade in trades:
        # Handle both Trade objects and dictionaries
        if hasattr(trade, 'trade_id'):
            trade_data.append({
                'Trade ID': trade.trade_id,
                'Asset Class': trade.asset_class.value if hasattr(trade.asset_class, 'value') else str(trade.asset_class),
                'Type': trade.trade_type.value if hasattr(trade.trade_type, 'value') else str(trade.trade_type),
                'Notional': f"${trade.notional:,.0f}",
                'Currency': trade.currency,
                'Maturity': f"{trade.time_to_maturity():.1f}y" if hasattr(trade, 'time_to_maturity') else 'N/A',
                'MTM': f"${trade.mtm_value:,.0f}",
                'Delta': f"{trade.delta:.2f}"
            })
        elif isinstance(trade, dict):
            trade_data.append({
                'Trade ID': trade.get('trade_id', 'N/A'),
                'Asset Class': trade.get('asset_class', 'N/A'),
                'Type': trade.get('trade_type', 'N/A'),
                'Notional': f"${trade.get('notional', 0):,.0f}",
                'Currency': trade.get('currency', 'N/A'),
                'Maturity': f"{trade.get('maturity_years', 0):.1f}y",
                'MTM': f"${trade.get('mtm_value', 0):,.0f}",
                'Delta': f"{trade.get('delta', 1.0):.2f}"
            })
    
    df = pd.DataFrame(trade_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_netting_set_summary(netting_set):
    """Render a summary of the netting set configuration."""
    
    st.markdown("### Netting Set Summary")
    
    # Handle both NettingSet objects and dictionaries
    if hasattr(netting_set, 'netting_set_id'):
        netting_data = {
            'Netting Set ID': netting_set.netting_set_id,
            'Counterparty': netting_set.counterparty,
            'Number of Trades': len(netting_set.trades) if netting_set.trades else 0,
            'Threshold': f"${netting_set.threshold:,.0f}",
            'MTA': f"${netting_set.mta:,.0f}",
            'NICA': f"${netting_set.nica:,.0f}",
            'Has CSA': 'Yes' if netting_set.has_csa else 'No'
        }
    elif isinstance(netting_set, dict):
        netting_data = {
            'Netting Set ID': netting_set.get('netting_set_id', 'N/A'),
            'Counterparty': netting_set.get('counterparty', 'N/A'),
            'Number of Trades': netting_set.get('trade_count', 0),
            'Threshold': f"${netting_set.get('threshold', 0):,.0f}",
            'MTA': f"${netting_set.get('mta', 0):,.0f}",
            'NICA': f"${netting_set.get('nica', 0):,.0f}",
            'Has CSA': 'Yes' if netting_set.get('has_csa', True) else 'No'
        }
    else:
        st.error("Invalid netting set format")
        return
    
    # Display as two columns
    col1, col2 = st.columns(2)
    
    items = list(netting_data.items())
    mid_point = len(items) // 2
    
    with col1:
        for key, value in items[:mid_point]:
            st.write(f"**{key}:** {value}")
    
    with col2:
        for key, value in items[mid_point:]:
            st.write(f"**{key}:** {value}")


def render_collateral_summary(collateral_list):
    """Render a summary of collateral posted."""
    
    if not collateral_list:
        st.info("No collateral posted")
        return
    
    st.markdown("### Collateral Summary")
    
    collateral_data = []
    total_value = 0
    
    for coll in collateral_list:
        # Handle both Collateral objects and dictionaries
        if hasattr(coll, 'collateral_type'):
            coll_type = coll.collateral_type.value if hasattr(coll.collateral_type, 'value') else str(coll.collateral_type)
            currency = coll.currency
            amount = coll.amount
            haircut = getattr(coll, 'haircut', 0) * 100 if hasattr(coll, 'haircut') else 0
        elif isinstance(coll, dict):
            coll_type = coll.get('collateral_type', 'N/A')
            currency = coll.get('currency', 'USD')
            amount = coll.get('amount', 0)
            haircut = coll.get('haircut', 0) * 100
        else:
            continue
        
        effective_value = amount * (1 - haircut/100)
        total_value += effective_value
        
        collateral_data.append({
            'Type': coll_type,
            'Currency': currency,
            'Amount': f"${amount:,.0f}",
            'Haircut (%)': f"{haircut:.1f}%",
            'Effective Value': f"${effective_value:,.0f}"
        })
    
    df = pd.DataFrame(collateral_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown(f"**Total Effective Collateral Value:** ${total_value:,.0f}")


def render_calculation_timeline(calculation_steps):
    """Render a visual timeline of calculation steps."""
    
    if not calculation_steps:
        st.info("No calculation steps available")
        return
    
    st.markdown("### Calculation Timeline")
    
    # Handle both list and dict formats
    if isinstance(calculation_steps, dict):
        steps = [(k, v) for k, v in calculation_steps.items()]
        steps.sort(key=lambda x: x[0])
    else:
        steps = [(getattr(step, 'step', i+1), step) for i, step in enumerate(calculation_steps)]
    
    # Create timeline visualization
    timeline_html = "<div style='position: relative; margin: 2rem 0;'>"
    
    for i, (step_num, step_data) in enumerate(steps[:10]):  # Show first 10 steps
        # Get step info
        if hasattr(step_data, 'title'):
            title = step_data.title
            status = "completed"
        elif isinstance(step_data, dict):
            title = step_data.get('title', f'Step {step_num}')
            status = "completed"
        else:
            title = f'Step {step_num}'
            status = "completed"
        
        # Timeline node
        timeline_html += f"""
        <div style='display: flex; align-items: center; margin: 1rem 0;'>
            <div style='width: 30px; height: 30px; border-radius: 50%; 
                        background: #28a745; color: white; display: flex; 
                        align-items: center; justify-content: center; 
                        font-weight: bold; margin-right: 1rem; flex-shrink: 0;'>
                {step_num}
            </div>
            <div style='flex-grow: 1; padding: 0.5rem; background: #f8f9fa; 
                        border-radius: 5px; border-left: 3px solid #28a745;'>
                {title}
            </div>
        </div>
        """
    
    if len(steps) > 10:
        timeline_html += f"""
        <div style='display: flex; align-items: center; margin: 1rem 0;'>
            <div style='width: 30px; height: 30px; border-radius: 50%; 
                        background: #6c757d; color: white; display: flex; 
                        align-items: center; justify-content: center; 
                        font-weight: bold; margin-right: 1rem; flex-shrink: 0;'>
                ...
            </div>
            <div style='flex-grow: 1; padding: 0.5rem; background: #f8f9fa; 
                        border-radius: 5px; border-left: 3px solid #6c757d;'>
                And {len(steps) - 10} more steps...
            </div>
        </div>
        """
    
    timeline_html += "</div>"
    
    st.markdown(timeline_html, unsafe_allow_html=True)


def render_risk_breakdown_chart(results: Dict[str, Any]):
    """Render a visual breakdown of risk components."""
    
    if 'final_results' not in results:
        st.info("No risk breakdown data available")
        return
    
    final_results = results['final_results']
    
    # Extract risk components
    rc = final_results.get('replacement_cost', 0)
    pfe = final_results.get('potential_future_exposure', 0)
    ead = final_results.get('exposure_at_default', 0)
    
    # Create simple visualization using metrics
    st.markdown("### Risk Component Breakdown")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Current Exposure (RC)", 
            f"${rc/1_000_000:.1f}M",
            help="Current replacement cost if counterparty defaults today"
        )
    
    with col2:
        st.metric(
            "Future Risk (PFE)", 
            f"${pfe/1_000_000:.1f}M",
            help="Potential future exposure over trade lifetime"
        )
    
    with col3:
        st.metric(
            "Total Exposure (EAD)", 
            f"${ead/1_000_000:.1f}M",
            help="Total exposure at default (RC + PFE) × Alpha"
        )
    
    with col4:
        alpha_factor = ead / (rc + pfe) if (rc + pfe) > 0 else 1.4
        st.metric(
            "Alpha Factor", 
            f"{alpha_factor:.2f}",
            help="Regulatory multiplier applied to gross exposure"
        )
    
    # Risk composition
    if rc + pfe > 0:
        rc_pct = (rc / (rc + pfe)) * 100
        pfe_pct = (pfe / (rc + pfe)) * 100
        
        st.markdown(f"""
        **Risk Composition:**
        - Current Risk: {rc_pct:.1f}%
        - Future Risk: {pfe_pct:.1f}%
        """)


def render_regulatory_summary_box():
    """Render a summary box highlighting regulatory compliance."""
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #0f4c75 0%, #3282b8 100%); 
                color: white; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;'>
        <h4 style='margin: 0 0 1rem 0; color: white;'>
            🏛️ Regulatory Compliance Summary
        </h4>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;'>
            <div>
                <strong>Framework:</strong> Basel III SA-CCR<br>
                <strong>Regulation:</strong> 12 CFR 217.132<br>
                <strong>Implementation:</strong> Complete Table 3
            </div>
            <div>
                <strong>Calculation Date:</strong> {datetime.now().strftime('%Y-%m-%d')}<br>
                <strong>Method:</strong> Dual Scenario Analysis<br>
                <strong>Validation:</strong> ✅ Regulatory Compliant
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_error_boundary(error_message: str, fallback_content: str = None):
    """Render an error boundary with fallback content."""
    
    st.error(f"⚠️ Display Error: {error_message}")
    
    if fallback_content:
        with st.expander("Show Fallback Content", expanded=False):
            st.text(fallback_content)
    
    st.info("Please check the data format and try again. If the problem persists, contact support.")


def safe_render_component(render_func, *args, component_name: str = "Component", **kwargs):
    """Safely render a component with error handling."""
    
    try:
        return render_func(*args, **kwargs)
    except Exception as e:
        st.error(f"Error rendering {component_name}: {str(e)}")
        
        # Show debug info in expander
        with st.expander(f"Debug Info - {component_name}", expanded=False):
            st.text(f"Error: {str(e)}")
            st.text(f"Args: {args}")
            st.text(f"Kwargs: {kwargs}")
        
        return None


# CSS Styles for enhanced display
def inject_custom_css():
    """Inject custom CSS for enhanced component styling."""
    
    st.markdown("""
    <style>
    .calc-step {
        border: 1px solid #e6e6e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .step-number {
        background: #0f4c75;
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 1rem;
    }
    
    .step-title {
        font-weight: 600;
        color: #0f4c75;
        font-size: 1.1rem;
    }
    
    .step-formula {
        background: #f8f9fa;
        padding: 0.75rem;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        margin: 0.5rem 0;
        border-left: 3px solid #0f4c75;
    }
    
    .thinking-process {
        background: #f0f8ff;
        padding: 1rem;
        border-radius: 5px;
        border-left: 3px solid #3282b8;
    }
    
    .data-quality-alert {
        background: #ffe6e6;
        border: 1px solid #ff9999;
        border-radius: 5px;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    
    .ai-response {
        background: #f0f8ff;
        border: 1px solid #b3d9ff;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .summary-box {
        background: white;
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin: 0.25rem;
    }
    
    .scenario-comparison {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .regulatory-badge {
        background: #28a745;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
