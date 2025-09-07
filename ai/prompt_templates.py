# ==============================================================================
# AI/PROMPT_TEMPLATES.PY - AI Prompt Templates
# ==============================================================================

"""
Structured prompt templates for SA-CCR AI analysis.
Contains system prompts and user prompt templates for different analysis types.
"""

from typing import Dict, List, Any

# ==============================================================================
# SYSTEM PROMPTS
# ==============================================================================

SACCR_EXPERT_SYSTEM_PROMPT = """You are a Basel SA-CCR regulatory expert with deep knowledge of:

**Technical Expertise:**
- Complete 24-step SA-CCR calculation methodology per Basel III framework
- Supervisory factors, correlations, and regulatory parameters by asset class
- PFE multiplier calculations and netting benefit mechanics
- Replacement cost calculations with margining and collateral considerations
- EAD, RWA, and capital requirement calculations
- Alpha multiplier applications and central clearing impacts

**Practical Experience:**
- Portfolio optimization strategies for SA-CCR capital efficiency
- Implementation challenges and solutions
- Data quality requirements and validation procedures
- Regulatory compliance and audit considerations
- Industry best practices and benchmarking

**Communication Style:**
- Provide detailed, technical answers with specific formulas and examples
- Include regulatory references to Basel framework sections where relevant
- Offer practical examples and scenarios to illustrate concepts
- Give actionable recommendations with quantified impacts when possible
- Explain complex concepts clearly for risk managers and practitioners

**Response Structure:**
- Start with direct answer to the question
- Provide technical explanation with formulas
- Include practical implementation guidance
- Offer optimization insights and recommendations
- Reference regulatory requirements and compliance considerations"""

PORTFOLIO_ANALYSIS_SYSTEM_PROMPT = """You are a derivatives portfolio optimization expert specializing in SA-CCR capital efficiency.

**Core Competencies:**
- Portfolio risk assessment and concentration analysis
- SA-CCR capital optimization strategies with quantified benefits
- Netting and collateral optimization techniques
- Trade structuring for regulatory capital efficiency
- Risk-return optimization within regulatory constraints

**Analysis Framework:**
1. Assess current portfolio risk profile and concentrations
2. Identify inefficiencies in SA-CCR capital calculation
3. Prioritize optimization opportunities by impact and feasibility
4. Provide specific, implementable recommendations
5. Quantify expected benefits and implementation complexity

**Focus Areas:**
- Portfolio composition and diversification effects
- Netting set optimization and master agreement strategies
- Collateral posting and CSA term optimization
- Central clearing economics and trade selection
- Trade compression and lifecycle management

**Deliverables:**
- Specific optimization recommendations with estimated capital impact
- Implementation roadmap with priority ranking
- Cost-benefit analysis including operational considerations
- Risk management implications and trade-offs
- Regulatory compliance and documentation requirements"""

OPTIMIZATION_SYSTEM_PROMPT = """You are a financial engineering expert focused on derivatives portfolio optimization for regulatory capital efficiency.

**Optimization Methodology:**
- Analyze current SA-CCR calculation results for inefficiencies
- Identify highest-impact optimization strategies
- Provide implementation guidance with realistic timelines
- Consider operational complexity and costs
- Ensure regulatory compliance throughout optimization process

**Key Optimization Levers:**
1. **Portfolio Structure:** Trade selection, notional sizing, maturity profiles
2. **Netting Enhancement:** Master agreement optimization, hedging set management
3. **Collateral Strategy:** CSA terms, collateral type selection, posting optimization
4. **Central Clearing:** CCP selection, clearing economics, trade lifecycle
5. **Risk Management:** Delta hedging, correlation benefits, concentration limits

**Analysis Output:**
- Top 3-5 optimization strategies ranked by impact
- Quantified capital savings estimates
- Implementation complexity assessment (Low/Medium/High)
- Timeline and resource requirements
- Regulatory and operational considerations
- Risk management implications

**Implementation Focus:**
- Practical, actionable recommendations
- Clear implementation steps and milestones
- Cost-benefit analysis with realistic assumptions
- Change management and operational impacts
- Monitoring and performance measurement frameworks"""

REGULATORY_COMMENTARY_SYSTEM_PROMPT = """You are a regulatory compliance expert specializing in Basel III SA-CCR implementation.

**Regulatory Expertise:**
- Basel III SA-CCR framework interpretation and application
- Jurisdictional differences and implementation variations
- Supervisory expectations and examination focus areas
- Model validation and governance requirements
- Regulatory reporting and documentation standards

**Compliance Focus:**
- Accuracy of calculation methodology
- Completeness of data and assumptions
- Audit trail and documentation quality
- Model risk management and controls
- Regulatory change management and updates

**Risk Assessment:**
- Model risk and validation concerns
- Data quality and completeness issues
- Operational risk and control weaknesses
- Regulatory examination readiness
- Industry benchmarking and peer comparison

**Guidance Areas:**
- Regulatory compliance best practices
- Documentation and audit trail requirements
- Model governance and validation frameworks
- Supervisory communication strategies
- Regulatory change impact assessment"""

STEP_EXPLANATION_SYSTEM_PROMPT = """You are a SA-CCR methodology expert focused on detailed step-by-step explanation of the Basel calculation framework.

**Teaching Approach:**
- Break down complex calculations into understandable components
- Explain the regulatory rationale behind each step
- Provide practical examples and real-world applications
- Connect individual steps to overall SA-CCR framework
- Highlight common implementation challenges and solutions

**Technical Depth:**
- Detailed formula explanations with parameter definitions
- Input data requirements and validation criteria
- Calculation dependencies and step sequencing
- Edge cases and special considerations
- Error checking and reasonableness testing

**Practical Guidance:**
- Implementation best practices for each step
- Common data sources and validation procedures
- Typical issues and troubleshooting approaches
- Optimization opportunities within each step
- Quality assurance and control frameworks

**Step Context:**
- How the step fits into the overall 24-step methodology
- Dependencies on previous steps and impact on subsequent steps
- Alternative calculation approaches and regulatory preferences
- Industry practices and implementation variations
- Future regulatory developments and potential changes"""

# ==============================================================================
# USER PROMPT TEMPLATES
# ==============================================================================

def create_saccr_explanation_prompt(enhanced_summary: Dict[str, Any],
                                   thinking_insights: List[str],
                                   assumptions: List[str],
                                   data_quality_issues: List) -> str:
    """Create prompt for comprehensive SA-CCR explanation."""
    
    assumptions_text = "\n".join(assumptions) if assumptions else "No significant assumptions"
    issues_summary = f"{len(data_quality_issues)} issues identified" if data_quality_issues else "No data quality issues"
    
    return f"""
Complete 24-step SA-CCR calculation performed with detailed analysis.

**CALCULATION SUMMARY:**
Key Inputs: {', '.join(enhanced_summary.get('key_inputs', []))}
Risk Components: {', '.join(enhanced_summary.get('risk_components', []))}
Capital Results: {', '.join(enhanced_summary.get('capital_results', []))}

**KEY CALCULATION INSIGHTS:**
{chr(10).join(thinking_insights)}

**DATA QUALITY ASSESSMENT:**
{issues_summary}

**CALCULATION ASSUMPTIONS:**
{assumptions_text}

**ANALYSIS REQUESTED:**
Provide executive-level analysis focusing on:

1. **Primary Capital Drivers:** What are the main factors driving the capital requirement and why?

2. **Optimization Opportunities:** What specific strategies would have the highest impact on reducing capital requirements? Provide quantified estimates where possible.

3. **Data Quality Impact:** How do the identified data quality issues affect calculation reliability? What improvements should be prioritized?

4. **Business Decisions:** What key business and risk management decisions should this analysis inform?

5. **Industry Context:** How does this portfolio profile compare to typical industry benchmarks?

Provide specific, actionable insights with quantified impacts and implementation guidance.
    """

def create_portfolio_analysis_prompt(portfolio_summary: Dict[str, Any]) -> str:
    """Create prompt for portfolio optimization analysis."""
    
    return f"""
Analyze this derivatives portfolio for SA-CCR capital optimization:

**PORTFOLIO CHARACTERISTICS:**
- Total Trades: {portfolio_summary.get('total_trades', 0)}
- Total Notional: ${portfolio_summary.get('total_notional', 0):,.0f}
- Asset Classes: {', '.join(portfolio_summary.get('asset_classes', []))}
- Currencies: {', '.join(portfolio_summary.get('currencies', []))}
- Average Maturity: {portfolio_summary.get('avg_maturity', 0):.1f} years
- Largest Trade: ${portfolio_summary.get('largest_trade', 0):,.0f}
- Net MTM Exposure: ${portfolio_summary.get('mtm_exposure', 0):,.0f}

**ANALYSIS REQUIREMENTS:**

1. **Portfolio Risk Assessment:**
   - Identify concentration risks and imbalances
   - Assess diversification benefits and gaps
   - Evaluate maturity profile optimization opportunities

2. **SA-CCR Capital Efficiency Analysis:**
   - Calculate current capital efficiency metrics
   - Identify primary capital drivers
   - Assess netting benefit realization

3. **Optimization Recommendations:**
   - Provide 3-5 specific optimization strategies
   - Estimate quantified capital savings for each
   - Rank by implementation complexity and impact

4. **Netting and Collateral Optimization:**
   - Evaluate current netting arrangements
   - Assess collateral posting optimization
   - Recommend CSA term improvements

5. **Implementation Roadmap:**
   - Prioritize actions by impact and feasibility
   - Provide realistic implementation timelines
   - Consider operational and regulatory constraints

Focus on practical, implementable strategies with quantified benefits and clear implementation guidance.
    """

def create_optimization_prompt(current_results: Dict[str, Any],
                              portfolio_characteristics: Dict[str, Any]) -> str:
    """Create prompt for specific optimization recommendations."""
    
    final_results = current_results.get('final_results', {})
    
    return f"""
Provide specific SA-CCR optimization recommendations based on current calculation results:

**CURRENT SA-CCR RESULTS:**
- Replacement Cost: ${final_results.get('replacement_cost', 0):,.0f}
- Potential Future Exposure: ${final_results.get('potential_future_exposure', 0):,.0f}
- Exposure at Default: ${final_results.get('exposure_at_default', 0):,.0f}
- Risk-Weighted Assets: ${final_results.get('risk_weighted_assets', 0):,.0f}
- Capital Requirement: ${final_results.get('capital_requirement', 0):,.0f}

**PORTFOLIO CONTEXT:**
{chr(10).join([f"- {k}: {v}" for k, v in portfolio_characteristics.items()])}

**OPTIMIZATION ANALYSIS REQUIRED:**

1. **Top 3 Optimization Strategies:**
   - Identify highest-impact optimization opportunities
   - Provide quantified capital impact estimates
   - Assess implementation feasibility and complexity

2. **Implementation Planning:**
   - Detailed implementation steps for each strategy
   - Realistic timeline and resource requirements
   - Risk management and operational considerations

3. **Regulatory Considerations:**
   - Compliance requirements and constraints
   - Documentation and approval processes
   - Supervisory communication needs

4. **Cost-Benefit Analysis:**
   - Implementation costs vs. capital savings
   - Operational impact and ongoing maintenance
   - Return on investment calculations

5. **Risk Management Implications:**
   - Impact on overall risk profile
   - Hedging and portfolio management effects
   - Unintended consequences and mitigation

Provide actionable recommendations with specific implementation guidance and quantified business impact.
    """

def create_step_explanation_prompt(step_number: int, 
                                  step_data: Dict[str, Any],
                                  context: Dict[str, Any] = None) -> str:
    """Create prompt for detailed step explanation."""
    
    context_info = ""
    if context:
        context_info = f"\n**CALCULATION CONTEXT:**\n{context}"
    
    return f"""
Provide detailed explanation for SA-CCR Step {step_number}:

**STEP DATA:**
{step_data}
{context_info}

**EXPLANATION REQUIREMENTS:**

1. **Regulatory Purpose:**
   - Why this step is required by Basel III SA-CCR
   - How it fits into the overall 24-step methodology
   - Regulatory rationale and policy objectives

2. **Calculation Methodology:**
   - Detailed breakdown of the calculation approach
   - Formula explanation with parameter definitions
   - Mathematical concepts and financial theory

3. **Key Inputs and Dependencies:**
   - Required input data and sources
   - Dependencies on previous calculation steps
   - Data quality requirements and validation

4. **Result Interpretation:**
   - What the calculated result represents
   - How it impacts the overall SA-CCR calculation
   - Typical ranges and benchmarks

5. **Common Issues and Considerations:**
   - Frequent implementation challenges
   - Edge cases and special situations
   - Quality assurance and error checking

6. **Optimization Opportunities:**
   - How this step can be optimized for capital efficiency
   - Portfolio management strategies
   - Structural and operational improvements

Keep the explanation technical but accessible to risk managers and practitioners.
    """

def create_regulatory_commentary_prompt(calculation_results: Dict[str, Any]) -> str:
    """Create prompt for regulatory compliance commentary."""
    
    final_results = calculation_results.get('final_results', {})
    
    return f"""
Provide regulatory compliance commentary on this SA-CCR calculation:

**CALCULATION RESULTS:**
- Exposure at Default: ${final_results.get('exposure_at_default', 0):,.0f}
- Risk-Weighted Assets: ${final_results.get('risk_weighted_assets', 0):,.0f}
- Capital Requirement: ${final_results.get('capital_requirement', 0):,.0f}

**REGULATORY ASSESSMENT REQUIRED:**

1. **Basel III SA-CCR Compliance:**
   - Adherence to 24-step calculation methodology
   - Proper application of supervisory parameters
   - Compliance with regulatory timing and frequency requirements

2. **Calculation Accuracy Review:**
   - Methodology implementation correctness
   - Data completeness and quality assessment
   - Formula application and parameter usage

3. **Regulatory Risk Assessment:**
   - Potential supervisory concerns or questions
   - Areas requiring additional documentation or justification
   - Model validation and governance considerations

4. **Documentation and Audit Readiness:**
   - Required documentation and audit trails
   - Model governance and control frameworks
   - Regulatory examination preparation

5. **Industry Benchmarking:**
   - Comparison to industry practices and results
   - Peer benchmarking and outlier analysis
   - Market context and reasonableness assessment

6. **Future Regulatory Developments:**
   - Upcoming regulatory changes and impacts
   - Industry consultation and implementation guidance
   - Strategic planning for regulatory evolution

Focus on regulatory compliance, audit readiness, and supervisory examination preparation.
    """

# ==============================================================================
# PROMPT UTILITIES
# ==============================================================================

def format_portfolio_context(portfolio_data: Dict[str, Any]) -> str:
    """Format portfolio context for inclusion in prompts."""
    if not portfolio_data:
        return "No portfolio context available."
    
    formatted_lines = []
    for key, value in portfolio_data.items():
        if isinstance(value, (int, float)):
            if key.lower().contains('notional') or key.lower().contains('amount'):
                formatted_lines.append(f"- {key.replace('_', ' ').title()}: ${value:,.0f}")
            else:
                formatted_lines.append(f"- {key.replace('_', ' ').title()}: {value}")
        elif isinstance(value, list):
            formatted_lines.append(f"- {key.replace('_', ' ').title()}: {', '.join(map(str, value))}")
        else:
            formatted_lines.append(f"- {key.replace('_', ' ').title()}: {value}")
    
    return "\n".join(formatted_lines)

def create_context_summary(results: Dict[str, Any]) -> str:
    """Create concise context summary for prompts."""
    final_results = results.get('final_results', {})
    
    return f"""
**Context Summary:**
- EAD: ${final_results.get('exposure_at_default', 0):,.0f}
- Capital: ${final_results.get('capital_requirement', 0):,.0f}
- Data Quality Issues: {len(results.get('data_quality_issues', []))}
- Assumptions Made: {len(results.get('assumptions', []))}
    """

def validate_prompt_inputs(prompt_type: str, **kwargs) -> List[str]:
    """Validate inputs for prompt generation."""
    issues = []
    
    if prompt_type == "saccr_explanation":
        required = ['enhanced_summary', 'thinking_insights']
        for req in required:
            if req not in kwargs or not kwargs[req]:
                issues.append(f"Missing required input: {req}")
    
    elif prompt_type == "portfolio_analysis":
        if 'portfolio_summary' not in kwargs:
            issues.append("Missing portfolio_summary")
        elif not kwargs['portfolio_summary'].get('total_trades', 0):
            issues.append("Portfolio summary contains no trades")
    
    elif prompt_type == "optimization":
        required = ['current_results', 'portfolio_characteristics']
        for req in required:
            if req not in kwargs:
                issues.append(f"Missing required input: {req}")
    
    return issues

# ==============================================================================
# EXPORT FOR USE IN OTHER MODULES
# ==============================================================================

__all__ = [
    'SACCR_EXPERT_SYSTEM_PROMPT',
    'PORTFOLIO_ANALYSIS_SYSTEM_PROMPT', 
    'OPTIMIZATION_SYSTEM_PROMPT',
    'REGULATORY_COMMENTARY_SYSTEM_PROMPT',
    'STEP_EXPLANATION_SYSTEM_PROMPT',
    'create_saccr_explanation_prompt',
    'create_portfolio_analysis_prompt',
    'create_optimization_prompt',
    'create_step_explanation_prompt',
    'create_regulatory_commentary_prompt',
    'format_portfolio_context',
    'create_context_summary',
    'validate_prompt_inputs'
]
