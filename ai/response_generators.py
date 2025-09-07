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
    """Generate response
