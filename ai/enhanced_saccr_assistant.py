# ==============================================================================
# ENHANCED SA-CCR AI ASSISTANT WITH CONVERSATIONAL CAPABILITIES
# ==============================================================================

"""
Enhanced AI Assistant for SA-CCR calculations with:
1. Complete regulatory knowledge of 12 CFR 217.132
2. 24-step calculation process expertise
3. Conversational human-in-the-loop capabilities
4. EAD estimation from natural language queries
"""

import streamlit as st
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from ai.llm_client import LLMClient
from calculations.saccr_engine import UnifiedSACCREngine
from models.trade import Trade
from models.netting_set import NettingSet
from models.enums import AssetClass, TradeType

class EnhancedSACCRAssistant:
    """Enhanced conversational SA-CCR assistant with regulatory expertise."""
    
    def __init__(self):
        """Initialize the enhanced assistant."""
        self.llm_client = LLMClient()
        self.saccr_engine = UnifiedSACCREngine()
        self.conversation_history = []
        self.current_context = {}
        
        # Regulatory knowledge base
        self.regulatory_context = self._build_regulatory_context()
        
    def _build_regulatory_context(self) -> str:
        """Build comprehensive regulatory context for the LLM."""
        return """
# US SA-CCR REGULATORY FRAMEWORK (12 CFR 217.132)

## COMPLETE 24-STEP CALCULATION PROCESS

### STEPS 1-6: Trade-Level Inputs
1. **Netting Set Data**: Counterparty ID, master agreement, netting set ID, position type, margin flag
2. **Asset Classification**: Map to asset class (IR, FX, Credit, Equity, Commodity), determine basis/volatility flags
3. **Hedging Set Determination**: Group trades by risk factors (IR by currency, FX by currency pair, etc.)
4. **Time Parameters (S, E, M)**: Settlement, end date, maturity in years from as-of date
5. **Adjusted Notional**: Apply supervisory duration formula: SD = max(0.05 * (exp(-0.05*S) - exp(-0.05*E)), 0.04)
6. **Maturity Factor**: MF_margined vs MF_unmargined based on MPOR (10 vs 20 business days)

### STEPS 7-10: Risk Factor Adjustments  
7. **Supervisory Delta**: +1/-1 for linear derivatives, actual delta for options per 12 CFR 217.132(c)(9)(iii)
8. **Supervisory Factor**: From Table 2 (IR=0.5%, FX=4%, Credit varies, Equity=20-32%, Commodity=18-40%)
9. **Adjusted Derivatives Contract Amount**: = Adjusted Notional × Delta × MF × SF
10. **Supervisory Correlation**: N/A for IR/FX, varies for Credit/Equity/Commodity per Table 2

### STEPS 11-16: Add-On Calculations
11. **Hedging Set Add-On**: Aggregate within hedging sets using correlation formulas
12. **Asset Class Add-On**: Sum hedging sets within each asset class  
13. **Aggregate Add-On**: Sum across all asset classes
14. **V, C Calculation**: Mark-to-market values (V) and collateral values (C)
15. **PFE Multiplier**: min(1, 0.05 + 0.95 * exp((V-C)/(2*0.95*AddOn))) per 12 CFR 217.132(c)(7)
16. **PFE**: Potential Future Exposure = PFE Multiplier × Aggregate Add-On

### STEPS 17-21: Exposure Calculation
17. **CSA Parameters**: Threshold (TH), Minimum Transfer Amount (MTA), Net Independent Collateral Amount (NICA)
18. **Replacement Cost**: RC_margined = max(V-C; TH+MTA-NICA; 0), RC_unmargined = max(V-C; 0)
19. **CEU Flag**: Central Bank Exposure flag (determines alpha multiplier)
20. **Alpha**: 1.0 if CEU=1, 1.4 if CEU=0 (US regulatory buffer)
21. **EAD**: Exposure at Default = Alpha × (RC + PFE), select minimum of margined/unmargined

### STEPS 22-24: Capital Calculation
22. **Counterparty Information**: Legal entity type, country, credit quality
23. **Risk Weight**: Per 12 CFR 217.32 (Corporate=100%, Bank=20%, Sovereign=0%)
24. **RWA**: Risk-Weighted Assets = Risk Weight × EAD; Capital = 8% × RWA

## REFERENCE EXAMPLE: LOWELL HOTEL PROPERTIES LLC
- Trade ID: 20BN474100
- Asset Class: Interest Rate
- Currency: USD
- Notional: $100,000,000
- Maturity: 8.33 years
- MTM: $8,382,419
- Final EAD: $11,790,314 (Unmargined scenario selected)
- RWA: $11,790,314 (100% risk weight)
- Capital: $943,225 (8% of RWA)
"""