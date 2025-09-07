# ==============================================================================
# AI ANALYSIS GENERATOR
# ai/analysis_generator.py
# ==============================================================================

"""
AI analysis generator for SA-CCR calculations and portfolio optimization.
Handles LLM integration for generating detailed SA-CCR explanations and insights.
"""

import json
from typing import Dict, List, Any, Optional
from langchain.schema import HumanMessage, SystemMessage

from ai.llm_client import LLMClient
from ai.prompt_templates import (
    SACCR_EXPERT_SYSTEM_PROMPT,
    PORTFOLIO_ANALYSIS_SYSTEM_PROMPT,
    OPTIMIZATION_SYSTEM_PROMPT
)


class AnalysisGenerator:
    """Generates AI-powered analysis for SA-CCR calculations and portfolios."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def generate_saccr_explanation(self, calculation_steps: List[Dict], 
                                  enhanced_summary: Dict[str, Any],
                                  thinking_steps: List[Dict] = None,
                                  assumptions: List[str] = None,
                                  data_quality_issues: List = None) -> Optional[str]:
        """
        Generate enhanced AI explanation of SA-CCR calculation results.
        
        Args:
            calculation_steps: List of calculation step results
            enhanced_summary: Summary of key inputs, risk components, and results
            thinking_steps: Detailed thinking process from calculation
            assumptions: List of assumptions made during calculation
            data_quality_issues: List of data quality issues identified
            
        Returns:
            AI-generated explanation or None if LLM unavailable
        """
        if not self.llm_client.is_connected():
            return None
        
        # Extract key insights from thinking steps
        key_thinking_insights = []
        if thinking_steps:
            for thinking_step in thinking_steps:
                if thinking_step.get('key_insight'):
                    key_thinking_insights.append(
                        f"Step {thinking_step['step']}: {thinking_step['key_insight']}"
                    )
        
        # Build comprehensive prompt
        user_prompt = self._build_saccr_explanation_prompt(
            enhanced_summary, key_thinking_insights, assumptions, data_quality_issues
        )
        
        try:
            response = self.llm_client.invoke([
                SystemMessage(content=SACCR_EXPERT_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ])
            return response
        except Exception as e:
            return f"Enhanced AI analysis temporarily unavailable: {str(e)}"
    
    def generate_portfolio_analysis(self, portfolio_summary: Dict[str, Any]) -> Optional[str]:
        """
        Generate AI-powered portfolio analysis and optimization recommendations.
        
        Args:
            portfolio_summary: Summary of portfolio characteristics
            
        Returns:
            AI-generated portfolio analysis or None if LLM unavailable
        """
        if not self.llm_client.is_connected():
            return None
        
        user_prompt = f"""
        Analyze this derivatives portfolio for SA-CCR capital optimization:
        
        Portfolio Summary:
        {json.dumps(portfolio_summary, indent=2)}
        
        Please provide:
        1. Portfolio risk assessment (concentrations, imbalances)
        2. SA-CCR capital efficiency analysis
        3. Specific optimization recommendations with estimated benefits
        4. Netting and collateral optimization opportunities
        5. Priority actions ranked by impact
        
        Focus on practical, implementable strategies with quantified benefits where possible.
        """
        
        try:
            response = self.llm_client.invoke([
                SystemMessage(content=PORTFOLIO_ANALYSIS_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ])
            return response
        except Exception as e:
            return f"Portfolio analysis temporarily unavailable: {str(e)}"
    
    def generate_optimization_recommendations(self, current_results: Dict[str, Any],
                                            portfolio_characteristics: Dict[str, Any]) -> Optional[str]:
        """
        Generate specific optimization recommendations based on current SA-CCR results.
        
        Args:
            current_results: Current SA-CCR calculation results
            portfolio_characteristics: Portfolio composition and characteristics
            
        Returns:
            AI-generated optimization recommendations
        """
        if not self.llm_client.is_connected():
            return None
        
        user_prompt = f"""
        Based on these SA-CCR calculation results and portfolio characteristics, 
        provide specific optimization recommendations:
        
        Current Results:
        - EAD: ${current_results['final_results']['exposure_at_default']:,.0f}
        - RWA: ${current_results['final_results']['risk_weighted_assets']:,.0f}
        - Capital: ${current_results['final_results']['capital_requirement']:,.0f}
        
        Portfolio Characteristics:
        {json.dumps(portfolio_characteristics, indent=2)}
        
        Provide:
        1. Top 3 optimization strategies with quantified impact
        2. Implementation complexity and timeline
        3. Regulatory considerations
        4. Cost-benefit analysis
        5. Risk management implications
        """
        
        try:
            response = self.llm_client.invoke([
                SystemMessage(content=OPTIMIZATION_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ])
            return response
        except Exception as e:
            return f"Optimization recommendations temporarily unavailable: {str(e)}"
    
    def generate_step_explanation(self, step_number: int, step_data: Dict[str, Any],
                                 context: Dict[str, Any] = None) -> Optional[str]:
        """
        Generate detailed explanation for a specific SA-CCR calculation step.
        
        Args:
            step_number: The step number (1-24)
            step_data: Data and results from the specific step
            context: Additional context from other steps
            
        Returns:
            AI-generated step explanation
        """
        if not self.llm_client.is_connected():
            return None
        
        user_prompt = f"""
        Explain SA-CCR Step {step_number} in detail:
        
        Step Data:
        {json.dumps(step_data, indent=2, default=str)}
        
        Please provide:
        1. Purpose and regulatory requirement for this step
        2. Detailed explanation of the calculation methodology
        3. Key inputs and their significance
        4. How the result impacts overall SA-CCR calculation
        5. Common issues or considerations for this step
        6. Optimization opportunities related to this step
        
        Keep the explanation technical but accessible to risk managers.
        """
        
        try:
            response = self.llm_client.invoke([
                SystemMessage(content=SACCR_EXPERT_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ])
            return response
        except Exception as e:
            return f"Step explanation temporarily unavailable: {str(e)}"
    
    def generate_regulatory_commentary(self, calculation_results: Dict[str, Any]) -> Optional[str]:
        """
        Generate regulatory commentary on the SA-CCR calculation.
        
        Args:
            calculation_results: Complete SA-CCR calculation results
            
        Returns:
            AI-generated regulatory commentary
        """
        if not self.llm_client.is_connected():
            return None
        
        user_prompt = f"""
        Provide regulatory commentary on this SA-CCR calculation:
        
        Key Results:
        - EAD: ${calculation_results['final_results']['exposure_at_default']:,.0f}
        - RWA: ${calculation_results['final_results']['risk_weighted_assets']:,.0f}
        - Capital: ${calculation_results['final_results']['capital_requirement']:,.0f}
        
        Please address:
        1. Compliance with Basel III SA-CCR requirements
        2. Accuracy of calculation methodology
        3. Potential regulatory concerns or questions
        4. Documentation and audit trail considerations
        5. Industry benchmarking context
        6. Future regulatory developments that may impact calculation
        
        Focus on regulatory compliance and audit readiness.
        """
        
        try:
            response = self.llm_client.invoke([
                SystemMessage(content=SACCR_EXPERT_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ])
            return response
        except Exception as e:
            return f"Regulatory commentary temporarily unavailable: {str(e)}"
    
    def _build_saccr_explanation_prompt(self, enhanced_summary: Dict[str, Any],
                                       key_thinking_insights: List[str],
                                       assumptions: List[str],
                                       data_quality_issues: List) -> str:
        """Build comprehensive prompt for SA-CCR explanation."""
        
        assumptions_text = "\n".join(assumptions) if assumptions else "No significant assumptions"
        issues_summary = f"{len(data_quality_issues)} issues identified" if data_quality_issues else "No data quality issues"
        
        return f"""
        Complete 24-step SA-CCR calculation performed with detailed thinking process analysis.
        
        ENHANCED SUMMARY:
        Key Inputs: {', '.join(enhanced_summary.get('key_inputs', []))}
        Risk Components: {', '.join(enhanced_summary.get('risk_components', []))}
        Capital Results: {', '.join(enhanced_summary.get('capital_results', []))}
        
        KEY THINKING INSIGHTS FROM CALCULATION:
        {chr(10).join(key_thinking_insights)}
        
        DATA QUALITY ASSESSMENT:
        {issues_summary}
        
        CALCULATION ASSUMPTIONS:
        {assumptions_text}
        
        Please provide executive analysis focusing on:
        1. What are the primary capital drivers and why?
        2. What optimization strategies would be most impactful?
        3. How do data quality issues affect the reliability of this calculation?
        4. What are the key business decisions this analysis should inform?
        5. How does this portfolio compare to typical industry profiles?
        
        Provide specific, actionable insights with quantified impacts where possible.
        """


# ==============================================================================
# STANDALONE FUNCTIONS FOR DIRECT USE
# ==============================================================================

def generate_saccr_explanation(calculation_steps: List[Dict], 
                              enhanced_summary: Dict[str, Any],
                              llm_client: LLMClient,
                              thinking_steps: List[Dict] = None,
                              assumptions: List[str] = None,
                              data_quality_issues: List = None) -> Optional[str]:
    """
    Standalone function to generate SA-CCR explanation.
    
    This function can be used directly without instantiating AnalysisGenerator.
    """
    generator = AnalysisGenerator(llm_client)
    return generator.generate_saccr_explanation(
        calculation_steps, enhanced_summary, thinking_steps, assumptions, data_quality_issues
    )


def generate_portfolio_analysis(portfolio_summary: Dict[str, Any], 
                               llm_client: LLMClient) -> Optional[str]:
    """
    Standalone function to generate portfolio analysis.
    
    This function can be used directly without instantiating AnalysisGenerator.
    """
    generator = AnalysisGenerator(llm_client)
    return generator.generate_portfolio_analysis(portfolio_summary)


def generate_optimization_recommendations(current_results: Dict[str, Any],
                                        portfolio_characteristics: Dict[str, Any],
                                        llm_client: LLMClient) -> Optional[str]:
    """
    Standalone function to generate optimization recommendations.
    """
    generator = AnalysisGenerator(llm_client)
    return generator.generate_optimization_recommendations(current_results, portfolio_characteristics)


def generate_step_explanation(step_number: int, step_data: Dict[str, Any],
                             llm_client: LLMClient, context: Dict[str, Any] = None) -> Optional[str]:
    """
    Standalone function to generate step-specific explanation.
    """
    generator = AnalysisGenerator(llm_client)
    return generator.generate_step_explanation(step_number, step_data, context)


# ==============================================================================
# ANALYSIS UTILITIES
# ==============================================================================

def extract_key_metrics_for_analysis(calculation_results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key metrics from calculation results for AI analysis."""
    final_results = calculation_results['final_results']
    
    # Find key steps
    steps = calculation_results['calculation_steps']
    step_15 = next((s for s in steps if s.step == 15), None)  # PFE Multiplier
    step_18 = next((s for s in steps if s.step == 18), None)  # RC
    step_21 = next((s for s in steps if s.step == 21), None)  # EAD
    
    return {
        'total_exposure': final_results['exposure_at_default'],
        'replacement_cost': final_results['replacement_cost'],
        'potential_future_exposure': final_results['potential_future_exposure'],
        'capital_requirement': final_results['capital_requirement'],
        'netting_benefit': (1 - step_15.data.get('multiplier', 1.0)) * 100 if step_15 else 0,
        'rc_vs_pfe_ratio': (final_results['replacement_cost'] / 
                           final_results['potential_future_exposure']) if final_results['potential_future_exposure'] > 0 else 0,
        'capital_efficiency': (final_results['capital_requirement'] / 
                              final_results['exposure_at_default']) * 100 if final_results['exposure_at_default'] > 0 else 0
    }


def identify_optimization_opportunities(calculation_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify specific optimization opportunities from calculation results."""
    opportunities = []
    
    final_results = calculation_results['final_results']
    steps = calculation_results['calculation_steps']
    
    # Find relevant steps
    step_15 = next((s for s in steps if s.step == 15), None)  # PFE Multiplier
    step_18 = next((s for s in steps if s.step == 18), None)  # RC
    
    # Check netting efficiency
    if step_15 and step_15.data.get('multiplier', 1.0) > 0.8:
        opportunities.append({
            'type': 'netting_enhancement',
            'description': 'Limited netting benefits - consider portfolio restructuring',
            'current_multiplier': step_15.data.get('multiplier', 1.0),
            'potential_benefit': 'High'
        })
    
    # Check margining status
    if step_18 and not step_18.data.get('is_margined', False):
        opportunities.append({
            'type': 'margining_implementation',
            'description': 'Unmargined netting set - implement CSA to reduce RC',
            'current_rc': final_results['replacement_cost'],
            'potential_benefit': 'Very High'
        })
    
    # Check exposure composition
    rc_pct = (final_results['replacement_cost'] / 
              (final_results['replacement_cost'] + final_results['potential_future_exposure']) * 100)
    
    if rc_pct > 70:
        opportunities.append({
            'type': 'current_exposure_reduction',
            'description': 'High current exposure dominance - consider collateral optimization',
            'current_rc_percentage': rc_pct,
            'potential_benefit': 'Medium'
        })
    
    return opportunities


def format_analysis_for_display(analysis_text: str) -> str:
    """Format AI analysis text for better display in Streamlit."""
    if not analysis_text:
        return "No analysis available"
    
    # Basic formatting improvements
    formatted = analysis_text.replace('\n\n', '\n\n**')
    formatted = formatted.replace('1.', '\n\n**1.**')
    formatted = formatted.replace('2.', '\n\n**2.**')
    formatted = formatted.replace('3.', '\n\n**3.**')
    formatted = formatted.replace('4.', '\n\n**4.**')
    formatted = formatted.replace('5.', '\n\n**5.**')
    
    return formatted


# ==============================================================================
# USAGE EXAMPLES
# ==============================================================================

"""
Example usage of the analysis generator:

# In a UI page or calculation result handler:
from ai.analysis_generator import generate_saccr_explanation, generate_portfolio_analysis

# Generate SA-CCR explanation
explanation = generate_saccr_explanation(
    calculation_steps=result['calculation_steps'],
    enhanced_summary=result['enhanced_summary'],
    llm_client=st.session_state.llm_client,
    thinking_steps=result.get('thinking_steps'),
    assumptions=result.get('assumptions'),
    data_quality_issues=result.get('data_quality_issues')
)

# Generate portfolio analysis
portfolio_summary = {
    'total_trades': len(trades),
    'total_notional': sum(abs(t.notional) for t in trades),
    'asset_classes': list(set(t.asset_class.value for t in trades)),
    # ... other portfolio characteristics
}

portfolio_analysis = generate_portfolio_analysis(
    portfolio_summary=portfolio_summary,
    llm_client=st.session_state.llm_client
)

# Display results
if explanation:
    st.markdown(f"### AI Analysis\n{explanation}")

if portfolio_analysis:
    st.markdown(f"### Portfolio Analysis\n{portfolio_analysis}")
"""
