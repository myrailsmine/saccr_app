# ==============================================================================
# UNIFIED SA-CCR ENGINE - COMPLETE 24-STEP IMPLEMENTATION
# Based on 12 CFR 217.132 and Reference Example (Lowell Hotel Properties LLC)
# ==============================================================================

"""
Complete 24-Step SA-CCR calculation engine implementing the exact methodology
from the regulatory document and reference example.

Reference Example:
- Trade ID: 20BN474100
- Counterparty: Lowell Hotel Properties LLC  
- Asset Class: Interest Rate
- Notional: $100,000,000
- As of Date: 2020-12-31
- Maturity: 2029-04-30 (8.33 years)
- MTM: $8,382,419
"""

import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from models.trade import Trade
from models.netting_set import NettingSet
from models.collateral import Collateral
from models.enums import AssetClass, TradeType, CollateralType

# ==============================================================================
# REGULATORY CONSTANTS PER 12 CFR 217.132 TABLE 3
# ==============================================================================

# Supervisory Factors (Table 2 to § 217.132)
SUPERVISORY_FACTORS = {
    AssetClass.INTEREST_RATE: {
        'all': 0.005  # 0.50% for all interest rate derivatives
    },
    AssetClass.FOREIGN_EXCHANGE: {
        'all': 0.04  # 4.0% for all exchange rate derivatives
    },
    AssetClass.CREDIT: {
        'single_name_investment_grade': 0.0046,
        'single_name_speculative_grade': 0.013,
        'single_name_sub_speculative_grade': 0.06,
        'index_investment_grade': 0.0038,
        'index_speculative_grade': 0.0106
    },
    AssetClass.EQUITY: {
        'single_name': 0.32,
        'index': 0.20
    },
    AssetClass.COMMODITY: {
        'energy_electricity': 0.40,
        'energy_other': 0.18,
        'metals': 0.18,
        'agricultural': 0.18,
        'other': 0.18
    }
}

# Supervisory Correlations (Table 2 to § 217.132)
SUPERVISORY_CORRELATIONS = {
    AssetClass.INTEREST_RATE: None,  # N/A
    AssetClass.FOREIGN_EXCHANGE: None,  # N/A
    AssetClass.CREDIT: {
        'single_name': 0.50,
        'index': 0.80
    },
    AssetClass.EQUITY: {
        'single_name': 0.50,
        'index': 0.80
    },
    AssetClass.COMMODITY: 0.40
}

# MPOR Values per 12 CFR 217.132
MPOR_VALUES = {
    'margined_standard': 10,    # 10 business days for margined transactions
    'margined_disputes': 20,    # 20 business days if disputes provision triggered
    'unmargined': 20           # 20 business days for unmargined transactions
}

# US Regulatory Constants
US_ALPHA_STANDARD = 1.4
US_ALPHA_CEU = 1.0  # For Central Bank exposures
US_CAPITAL_RATIO = 0.08
BUSINESS_DAYS_PER_YEAR = 250

# ==============================================================================
# UNIFIED SA-CCR ENGINE CLASS
# ==============================================================================

@dataclass
class CalculationStep:
    """Represents a single calculation step with detailed information."""
    step: int
    title: str
    description: str
    formula: str
    result: Any
    data: Dict[str, Any]
    thinking: Optional[Dict[str, str]] = None

class UnifiedSACCREngine:
    """
    Complete 24-step SA-CCR calculation engine following the exact methodology
    from the regulatory document and 12 CFR 217.132.
    """
    
    def __init__(self, as_of_date: datetime = None):
        """Initialize the SA-CCR engine."""
        self.as_of_date = as_of_date or datetime(2020, 12, 31)
        self.calculation_steps: List[CalculationStep] = []
        self.shared_data: Dict[str, Any] = {}