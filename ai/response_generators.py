# ==============================================================================
# AI/RESPONSE_GENERATORS.PY - Template Response Generators
# ==============================================================================

"""
Template response generators for SA-CCR questions when LLM is unavailable.
Provides fallback responses for common SA-CCR topics and questions.
"""

from typing import Dict, List, Optional, Any
import re


def generate_template_response(question: str, portfolio_context: Dict[str, Any] = None) -> str:
    """
    Generate template response for SA-CCR questions when LLM is unavailable.
    
    Args:
        question: User's question about SA-CCR
        portfolio_context: Optional portfolio information for context
        
    Returns:
        Template response string
    """
    question_lower = question.lower()
    
    # Analyze question type and generate appropriate response
    if _is_pfe_multiplier_question(question_lower):
        return _generate_pfe_multiplier_response(portfolio_context)
    
    elif _is_replacement_cost_question(question_lower):
        return _generate_replacement_cost_response(portfolio_context)
    
    elif _is_optimization_question(question_lower):
        return _generate_optimization_response(portfolio_context)
    
    elif _is_methodology_question(question_lower):
        return _generate_methodology_response()
    
    elif _is_regulatory_question(question_lower):
        return _generate_regulatory_response()
    
    elif _is_alpha_multiplier_question(question_lower):
        return _generate_alpha_multiplier_response()
    
    elif _is_supervisory_factors_question(question_lower):
        return _generate_supervisory_factors_response()
    
    elif _is_netting_question(question_lower):
        return _generate_netting_response(portfolio_context)
    
    elif _is_collateral_question(question_lower):
        return _generate_collateral_response()
    
    elif _is_central_clearing_question(question_lower):
        return _generate_central_clearing_response()
    
    else:
        return _generate_general_response(portfolio_context)


# ==============================================================================
# QUESTION TYPE DETECTION
# ==============================================================================

def _is_pfe_multiplier_question(question: str) -> bool:
    """Check if question is about PFE multiplier."""
    keywords = ["pfe multiplier", "multiplier", "netting benefit", "step 15", "0.05 + 0.95"]
    return any(keyword in question for keyword in keywords)

def _is_replacement_cost_question(question: str) -> bool:
    """Check if question is about replacement cost."""
    keywords = ["replacement cost", "rc", "margined", "unmargined", "threshold", "mta", "step 18"]
    return any(keyword in question for keyword in keywords)

def _is_optimization_question(question: str) -> bool:
    """Check if question is about optimization."""
    keywords = ["optimization", "optimize", "reduce capital", "reduce exposure", "strategy", "improve"]
    return any(keyword in question for keyword in keywords)

def _is_methodology_question(question: str) -> bool:
    """Check if question is about methodology."""
    keywords = ["24 step", "methodology", "calculation", "process", "how does", "walk through"]
    return any(keyword in question for keyword in keywords)

def _is_regulatory_question(question: str) -> bool:
    """Check if question is about regulatory aspects."""
    keywords = ["basel", "regulation", "compliance", "regulatory", "framework", "requirement"]
    return any(keyword in question for keyword in keywords)

def _is_alpha_multiplier_question(question: str) -> bool:
    """Check if question is about alpha multiplier."""
    keywords = ["alpha", "1.4", "step 20", "multiplier", "central clearing"]
    return any(keyword in question for keyword in keywords)

def _is_supervisory_factors_question(question: str) -> bool:
    """Check if question is about supervisory factors."""
    keywords = ["supervisory factor", "volatility", "asset class", "step 8", "correlation"]
    return any(keyword in question for keyword in keywords)

def _is_netting_question(question: str) -> bool:
    """Check if question is about netting."""
    keywords = ["netting", "hedging set", "portfolio", "diversification", "correlation"]
    return any(keyword in question for keyword in keywords)

def _is_collateral_question(question: str) -> bool:
    """Check if question is about collateral."""
    keywords = ["collateral", "haircut", "csa", "margin", "security"]
    return any(keyword in question for keyword in keywords)

def _is_central_clearing_question(question: str) -> bool:
    """Check if question is about central clearing."""
    keywords = ["central clearing", "ccp", "cleared", "ceu flag", "step 19"]
    return any(keyword in question for keyword in keywords)


# ==============================================================================
# RESPONSE GENERATORS
# ==============================================================================

def _generate_pfe_multiplier_response(portfolio_context: Dict = None) -> str:
    """Generate response about PFE multiplier."""
    context_info = ""
    if portfolio_context and portfolio_context.get('trade_count', 0) > 0:
        context_info = f"\n\nFor your current portfolio of {portfolio_context['trade_count']} trades, the multiplier will depend on the net MTM value relative to the aggregate add-on."
    
    return f"""
**PFE Multiplier Explanation:**

The PFE Multiplier is a key component in SA-CCR that captures netting benefits within a netting set.

**Formula:**
Multiplier = min(1, 0.05 + 0.95 × exp(-0.05 × max(0, V) / aggregate_addon))

**Key Drivers:**
- **V**: Net MTM of all trades in the netting set
- **Aggregate Add-on**: Sum of all asset class add-ons
- **Ratio V/AddOn**: Higher ratios reduce the multiplier (more netting benefit)

**Practical Impact:**
- Multiplier ranges from 0.05 to 1.0
- Lower multipliers = more netting benefit = lower capital
- When V is negative (out-of-the-money), multiplier approaches minimum 0.05
- When V >> AddOn, multiplier approaches 1.0 (no netting benefit)

**Optimization Strategy:**
Balance your portfolio MTM through strategic hedging to maximize netting benefits.{context_info}
    """

def _generate_replacement_cost_response(portfolio_context: Dict = None) -> str:
    """Generate response about replacement cost."""
    return """
**Replacement Cost (RC) Calculation:**

RC differs significantly between margined and unmargined netting sets.

**Margined Netting Sets:**
RC = max(V - C, TH + MTA - NICA, 0)

**Unmargined Netting Sets:**
RC = max(V - C, 0)

**Key Components:**
- **V**: Current market value (sum of trade MTMs)
- **C**: Effective collateral value after haircuts
- **TH**: Threshold amount
- **MTA**: Minimum Transfer Amount
- **NICA**: Net Independent Collateral Amount

**Critical Differences:**
- Margined: RC can never be less than TH + MTA - NICA
- Unmargined: RC simply equals positive net exposure
- Margined sets typically have lower RC due to collateral posting

**Optimization:**
- Negotiate lower thresholds and MTAs
- Post high-quality collateral with low haircuts
- Consider central clearing for eligible trades
    """

def _generate_optimization_response(portfolio_context: Dict = None) -> str:
    """Generate response about SA-CCR optimization."""
    portfolio_info = ""
    if portfolio_context:
        total_notional = portfolio_context.get('total_notional', 0)
        asset_classes = portfolio_context.get('asset_classes', [])
        currencies = portfolio_context.get('currencies', [])
        
        portfolio_info = f"""
**Your Portfolio Context:**
- Total Notional: ${total_notional/1_000_000:.0f}M
- Asset Classes: {', '.join(asset_classes)}
- Currencies: {', '.join(currencies)}
"""
    
    return f"""
**SA-CCR Capital Optimization Strategies:**

**1. Portfolio Structure (15-30% capital reduction)**
- Balance long/short positions to reduce net MTM
- Diversify across asset classes to benefit from correlations
- Consider trade compression to reduce gross notional

**2. Netting Enhancement (20-40% reduction)**
- Consolidate trading relationships under master agreements
- Negotiate cross-product netting where possible
- Ensure legal enforceability in all jurisdictions

**3. Collateral Optimization (30-60% reduction)**
- Post high-quality collateral (government bonds vs. equities)
- Minimize currency mismatches to avoid FX haircuts
- Negotiate lower thresholds and MTAs

**4. Central Clearing (50%+ reduction)**
- Clear eligible trades to benefit from Alpha = 1.4 vs. higher multipliers
- Consider portfolio-level clearing strategies

**5. Trade Structure Optimization**
- Use shorter maturities where possible (better maturity factors)
- Consider option structures vs. linear trades
- Optimize delta exposure for option positions

**Expected Combined Impact:** 40-70% capital reduction with comprehensive optimization
{portfolio_info}
    """

def _generate_methodology_response() -> str:
    """Generate response about SA-CCR methodology."""
    return """
**SA-CCR 24-Step Methodology Overview:**

**Steps 1-5: Data Preparation**
1. Netting Set Data Collection
2. Asset Class Classification
3. Hedging Set Determination
4. Time Parameters (S, E, M)
5. Adjusted Notional Calculation

**Steps 6-10: Risk Factor Processing**
6. Maturity Factor (MF)
7. Supervisory Delta
8. Supervisory Factor (SF)
9. Adjusted Derivatives Contract Amount
10. Supervisory Correlation

**Steps 11-16: Add-On Calculations**
11. Hedging Set AddOn
12. Asset Class AddOn
13. Aggregate AddOn
14. Sum of V, C
15. PFE Multiplier
16. Potential Future Exposure (PFE)

**Steps 17-21: Exposure Calculations**
17. Threshold, MTA, NICA
18. Replacement Cost (RC)
19. CEU Flag
20. Alpha Multiplier
21. Exposure at Default (EAD)

**Steps 22-24: Capital Requirements**
22. Counterparty Information
23. Risk Weight
24. Risk-Weighted Assets (RWA)

**Key Formula:**
EAD = Alpha × (RC + PFE)
Capital = RWA × 8%
    """

def _generate_regulatory_response() -> str:
    """Generate response about regulatory aspects."""
    return """
**Basel III SA-CCR Regulatory Framework:**

**Purpose:**
SA-CCR (Standardized Approach for Counterparty Credit Risk) is the Basel III framework for calculating exposure at default for derivative transactions.

**Key Regulatory Requirements:**
- Mandatory for all banks under Basel III
- Replaces previous methods (Current Exposure Method, etc.)
- Applies to OTC derivatives, exchange-traded derivatives, and long settlement transactions

**Compliance Considerations:**
- Must follow exact 24-step methodology
- Requires accurate trade and collateral data
- Need proper documentation and audit trails
- Regular validation and back-testing required

**Implementation Timeline:**
- Effective January 1, 2017 (with jurisdictional variations)
- Full implementation required by most regulators
- Ongoing updates and clarifications from Basel Committee

**Documentation Requirements:**
- Detailed calculation methodology
- Data sources and validation procedures
- Model governance and controls
- Regular reporting to regulators

**Key Benefits:**
- More risk-sensitive than previous approaches
- Better recognition of netting and collateral
- Standardized across jurisdictions
    """

def _generate_alpha_multiplier_response() -> str:
    """Generate response about alpha multiplier."""
    return """
**Alpha Multiplier in SA-CCR:**

**Purpose:**
Alpha is a regulatory scaling factor applied to the total exposure (RC + PFE) to determine the final Exposure at Default (EAD).

**Value:**
Alpha = 1.4 (fixed value in SA-CCR)

**Application:**
EAD = Alpha × (RC + PFE)
EAD = 1.4 × (Replacement Cost + Potential Future Exposure)

**Regulatory Rationale:**
- Provides additional conservatism in exposure calculation
- Accounts for potential model uncertainty
- Ensures adequate capital coverage for counterparty risk
- Consistent with stress testing and economic capital approaches

**Impact on Capital:**
- Increases final exposure by 40%
- Applied after all netting and collateral benefits
- Cannot be reduced through optimization
- Same for all asset classes and trade types

**Note:** Some jurisdictions may apply different alpha values for specific circumstances (e.g., centrally cleared trades), but the standard SA-CCR uses 1.4.
    """

def _generate_supervisory_factors_response() -> str:
    """Generate response about supervisory factors."""
    return """
**Supervisory Factors in SA-CCR:**

**Purpose:**
Supervisory factors represent regulatory estimates of asset price volatility over a one-year horizon at 99% confidence level.

**Key Categories:**

**Interest Rate (by currency and maturity):**
- USD/EUR/JPY/GBP: 0.5% (<2y), 0.5% (2-5y), 1.5% (>5y)
- Other currencies: 1.5% (all maturities)

**Foreign Exchange:**
- G10 currencies: 4.0%
- Emerging currencies: 15.0%

**Credit:**
- Investment Grade single names: 0.46%
- High Yield single names: 1.30%
- Investment Grade indices: 0.38%
- High Yield indices: 1.06%

**Equity:**
- Large cap single names: 32%
- Small cap single names: 40%
- Developed market indices: 20%
- Emerging market indices: 25%

**Commodity:**
- Energy: 18%
- Metals: 18%
- Agriculture: 18%
- Other: 18%

**Usage:**
These factors are multiplied by the adjusted notional to calculate risk-weighted exposure for each trade.

**Optimization Impact:**
Cannot be changed, but portfolio composition affects weighted average supervisory factor.
    """

def _generate_netting_response(portfolio_context: Dict = None) -> str:
    """Generate response about netting benefits."""
    context_info = ""
    if portfolio_context and portfolio_context.get('asset_classes'):
        asset_classes = portfolio_context['asset_classes']
        context_info = f"\n\nYour portfolio includes {', '.join(asset_classes)}, which may provide netting benefits through supervisory correlations."
    
    return f"""
**Netting Benefits in SA-CCR:**

**Hedging Set Level:**
- Trades are grouped by asset class and risk factor
- Direct offsetting within each hedging set
- Linear aggregation of effective notionals

**Asset Class Level:**
- Uses supervisory correlations between hedging sets
- Formula: sqrt((ρ × ΣA)² + (1-ρ²) × Σ(A²))
- Higher correlations = more netting benefit

**Supervisory Correlations:**
- Interest Rate: 99% (very high netting)
- Equity: 80% (high netting)
- Foreign Exchange: 60% (moderate netting)
- Credit: 50% (moderate netting)
- Commodity: 40% (lower netting)

**Portfolio Level (PFE Multiplier):**
- Captures overall netting benefit
- Based on current MTM vs. future risk
- Can reduce PFE by up to 95%

**Optimization Strategies:**
- Diversify across asset classes with high correlations
- Balance long/short positions
- Maintain offsetting positions in same hedging sets
- Consider the directional exposure (delta) of trades{context_info}
    """

def _generate_collateral_response() -> str:
    """Generate response about collateral."""
    return """
**Collateral in SA-CCR:**

**Role in RC Calculation:**
RC = max(V - C, TH + MTA - NICA, 0) for margined netting sets
Where C = effective collateral value after haircuts

**Collateral Haircuts:**
- Cash: 0%
- Government bonds: 0.5%
- Corporate bonds: 4.0%
- Equities: 15%
- Money market funds: 0.5%

**Optimization Strategies:**
- Use high-quality collateral (cash, government bonds)
- Match collateral currency to trade currency
- Minimize haircuts through collateral selection
- Negotiate favorable CSA terms

**CSA Terms Impact:**
- Lower thresholds reduce RC
- Lower MTAs reduce RC
- Bilateral vs. unilateral posting
- Rehypothecation rights

**Best Practices:**
- Regular collateral valuation
- Efficient collateral management systems
- Monitor concentration limits
- Consider operational costs vs. capital benefits
    """

def _generate_central_clearing_response() -> str:
    """Generate response about central clearing."""
    return """
**Central Clearing in SA-CCR:**

**CEU Flag (Step 19):**
- CEU = 0 for centrally cleared trades
- CEU = 1 for non-centrally cleared trades

**Impact on Alpha (Step 20):**
- Standard SA-CCR: Alpha = 1.4
- Some jurisdictions may apply lower alpha for cleared trades
- Check local regulatory requirements

**Benefits of Central Clearing:**
- Potential for lower alpha multiplier
- Reduced counterparty risk
- Standardized margining
- Daily variation margin
- Regulatory capital relief

**Eligible Products:**
- Interest rate swaps
- Credit default swaps
- Some FX derivatives
- Equity derivatives (selected)

**Considerations:**
- CCP membership requirements
- Initial margin requirements
- Operational complexity
- Basis risk between cleared and uncleared

**Optimization Strategy:**
Clear eligible trades where economically beneficial, considering:
- Capital savings from lower alpha
- Initial margin costs
- Operational expenses
- Portfolio composition effects
    """

def _generate_general_response(portfolio_context: Dict = None) -> str:
    """Generate general SA-CCR guidance."""
    portfolio_info = ""
    if portfolio_context and portfolio_context.get('trade_count', 0) > 0:
        portfolio_info = f"""
**Your Current Portfolio:**
- {portfolio_context['trade_count']} trades
- Total notional: ${portfolio_context.get('total_notional', 0)/1_000_000:.0f}M
"""
    
    return f"""
**SA-CCR Expert Guidance:**

I can help you understand the complete Basel SA-CCR framework including:

**Technical Areas:**
- All 24 calculation steps with detailed formulas
- Supervisory factors and correlations by asset class
- PFE multiplier mechanics and optimization
- Replacement cost calculation differences
- Alpha multiplier impacts from central clearing

**Practical Applications:**
- Portfolio optimization strategies
- Capital efficiency improvements
- Regulatory compliance requirements
- Implementation best practices

**Common Topics:**
- "How does the PFE multiplier work?"
- "What's the difference between margined and unmargined RC?"
- "How can I optimize my portfolio to reduce capital?"
- "Walk me through the 24-step methodology"
- "What are supervisory factors and how are they used?"

**Please ask specific questions about:**
- Calculation steps or formulas
- Portfolio optimization strategies
- Regulatory compliance requirements
- Implementation challenges
{portfolio_info}

This will help me provide more targeted and actionable guidance for your SA-CCR implementation.
    """


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def get_relevant_keywords(question: str) -> List[str]:
    """Extract relevant SA-CCR keywords from question."""
    saccr_keywords = [
        'pfe', 'multiplier', 'replacement cost', 'alpha', 'supervisory factor',
        'netting', 'hedging set', 'correlation', 'collateral', 'threshold',
        'mta', 'nica', 'central clearing', 'ceu flag', 'asset class',
        'maturity factor', 'delta', 'add-on', 'ead', 'rwa', 'capital'
    ]
    
    question_lower = question.lower()
    found_keywords = []
    
    for keyword in saccr_keywords:
        if keyword in question_lower:
            found_keywords.append(keyword)
    
    return found_keywords

def estimate_response_quality(question: str, portfolio_context: Dict = None) -> str:
    """Estimate the quality/relevance of template response."""
    keywords = get_relevant_keywords(question)
    
    if len(keywords) >= 3:
        return "high"
    elif len(keywords) >= 1:
        return "medium"
    else:
        return "low"

def suggest_llm_connection(question: str) -> bool:
    """Suggest whether LLM connection would significantly improve response."""
    complex_indicators = [
        'compare', 'analyze', 'quantify', 'calculate', 'specific',
        'detailed', 'comprehensive', 'impact', 'strategy'
    ]
    
    question_lower = question.lower()
    return any(indicator in question_lower for indicator in complex_indicators)
