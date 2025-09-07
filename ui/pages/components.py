# ui/components.py
"""Reusable UI components for the SA-CCR application."""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any

from utils.data_export import create_summary_csv, create_steps_csv


def display_calculation_results(result: Dict[str, Any]):
    """Display comprehensive SA-CCR calculation results."""
    
    # Final Results Summary
    st.markdown("## SA-CCR Calculation Results")
    
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
    
    # Enhanced Summary
    if 'enhanced_summary' in result:
        _display_enhanced_summary(result['enhanced_summary'])
    
    # Detailed Step-by-Step Breakdown
    _display_calculation_steps(result['calculation_steps'])
    
    # Data Quality Issues
    if result.get('data_quality_issues'):
        _display_data_quality_issues(result['data_quality_issues'])
    
    # AI Analysis
    if result.get('ai_explanation'):
        _display_ai_analysis(result['ai_explanation'])
    
    # Export Options
    _display_export_options(result)


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
    """Display detailed calculation steps."""
    with st.expander("🔍 Complete 24-Step Calculation Breakdown", expanded=False):
        
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
                        
                        st.markdown(f"""
                        <div class="calc-step">
                            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                                <span class="step-number">{step_data.step}</span>
                                <span class="step-title">{step_data.title}</span>
                            </div>
                            <div style="margin-bottom: 0.5rem;">
                                <strong>Description:</strong> {step_data.description}
                            </div>
                            <div class="step-formula">{step_data.formula}</div>
                            <div style="font-size: 1.1rem; font-weight: 600; color: #0f4c75; margin-top: 0.5rem;">
                                <strong>Result:</strong> {step_data.result}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show thinking process if available
                        if hasattr(step_data, 'thinking') and step_data.thinking:
                            with st.expander(f"💭 Thinking Process - Step {step_num}", expanded=False):
                                st.markdown(f"""
                                <div class="thinking-process">
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
                <div class="data-quality-alert">
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


def _display_ai_analysis(ai_explanation):
    """Display AI analysis if available."""
    if ai_explanation:
        st.markdown("### 🤖 AI Expert Analysis")
        st.markdown(f"""
        <div class="ai-response">
            {ai_explanation}
        </div>
        """, unsafe_allow_html=True)


def _display_export_options(result):
    """Display export options for results."""
    st.markdown("### 📥 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        summary_csv = create_summary_csv(result)
        st.download_button(
            "📊 Download Summary CSV",
            data=summary_csv,
            file_name=f"saccr_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        steps_csv = create_steps_csv(result['calculation_steps'])
        st.download_button(
            "📋 Download Steps CSV",
            data=steps_csv,
            file_name=f"saccr_steps_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col3:
        json_data = json.dumps(result, indent=2, default=str)
        st.download_button(
            "🔧 Download JSON",
            data=json_data,
            file_name=f"saccr_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


def render_metric_card(title: str, value: str, delta: str = None, help_text: str = None):
    """Render a custom metric card."""
    delta_html = f"<div style='color: #28a745; font-size: 0.8rem;'>{delta}</div>" if delta else ""
    help_html = f"<div style='color: #6c757d; font-size: 0.7rem; margin-top: 0.5rem;'>{help_text}</div>" if help_text else ""
    
    st.markdown(f"""
    <div class="summary-box">
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
    summary_data = {
        'Metric': [
            'Replacement Cost (RC)',
            'Potential Future Exposure (PFE)', 
            'Exposure at Default (EAD)',
            'Risk-Weighted Assets (RWA)',
            'Capital Requirement'
        ],
        'Value ($M)': [
            f"{results['final_results']['replacement_cost']/1_000_000:.2f}",
            f"{results['final_results']['potential_future_exposure']/1_000_000:.2f}",
            f"{results['final_results']['exposure_at_default']/1_000_000:.2f}",
            f"{results['final_results']['risk_weighted_assets']/1_000_000:.2f}",
            f"{results['final_results']['capital_requirement']/1_000_000:.2f}"
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
    if validation_result['is_complete']:
        st.success("✅ All required inputs provided")
    else:
        st.error("❌ Missing required information:")
        for field in validation_result['missing_fields']:
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
    
    # Step selector
    step_options = [f"Step {step.step}: {step.title}" for step in calculation_steps]
    selected_idx = st.selectbox("Select Step to View:", range(len(step_options)), 
                               format_func=lambda x: step_options[x],
                               index=selected_step-1 if selected_step and selected_step <= len(calculation_steps) else 0)
    
    if selected_idx < len(calculation_steps):
        step = calculation_steps[selected_idx]
        
        # Display step details
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {step.title}")
            st.markdown(step.description)
            
            with st.expander("Formula & Calculation", expanded=True):
                st.code(step.formula, language="text")
                st.markdown(f"**Result:** {step.result}")
        
        with col2:
            if hasattr(step, 'thinking') and step.thinking:
                with st.expander("💭 Thinking Process", expanded=False):
                    st.markdown(step.thinking.get('reasoning', 'No reasoning available'))
                    if step.thinking.get('key_insight'):
                        st.info(f"**Key Insight:** {step.thinking['key_insight']}")
        
        # Display step data if available
        if step.data and isinstance(step.data, dict):
            with st.expander("📊 Step Data", expanded=False):
                st.json(step.data)


def render_trade_comparison_table(trades):
    """Render a comparison table of trades."""
    if not trades:
        st.info("No trades to display")
        return
    
    trade_data = []
    for trade in trades:
        trade_data.append({
            'Trade ID': trade.trade_id,
            'Asset Class': trade.asset_class.value,
            'Type': trade.trade_type.value,
            'Notional': f"${trade.notional:,.0f}",
            'Currency': trade.currency,
            'Maturity': f"{trade.time_to_maturity():.1f}y",
            'MTM': f"${trade.mtm_value:,.0f}",
            'Delta': f"{trade.delta:.2f}"
        })
    
    df = pd.DataFrame(trade_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
