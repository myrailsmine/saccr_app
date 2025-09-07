"""Basel SA-CCR regulatory parameters and supervisory factors."""

from enum import Enum
from typing import Dict, Any

class AssetClass(Enum):
    INTEREST_RATE = "Interest Rate"
    FOREIGN_EXCHANGE = "Foreign Exchange" 
    CREDIT = "Credit"
    EQUITY = "Equity"
    COMMODITY = "Commodity"

class TradeType(Enum):
    SWAP = "Swap"
    FORWARD = "Forward"
    OPTION = "Option"
    SWAPTION = "Swaption"

class CollateralType(Enum):
    CASH = "Cash"
    GOVERNMENT_BONDS = "Government Bonds"
    CORPORATE_BONDS = "Corporate Bonds"
    EQUITIES = "Equities"
    MONEY_MARKET = "Money Market Funds"

# Supervisory Factors (in basis points) - EXACT Basel values
SUPERVISORY_FACTORS = {
    AssetClass.INTEREST_RATE: {
        'USD': {'<2y': 50.0, '2-5y': 50.0, '>5y': 150.0},
        'EUR': {'<2y': 50.0, '2-5y': 50.0, '>5y': 150.0},
        'JPY': {'<2y': 50.0, '2-5y': 50.0, '>5y': 150.0}, 
        'GBP': {'<2y': 50.0, '2-5y': 50.0, '>5y': 150.0},
        'other': {'<2y': 150.0, '2-5y': 150.0, '>5y': 150.0}
    },
    AssetClass.FOREIGN_EXCHANGE: {'G10': 400.0, 'emerging': 1500.0},
    AssetClass.CREDIT: {
        'IG_single': 46.0, 'HY_single': 130.0,
        'IG_index': 38.0, 'HY_index': 106.0
    },
    AssetClass.EQUITY: {
        'single_large': 3200.0, 'single_small': 4000.0,
        'index_developed': 2000.0, 'index_emerging': 2500.0
    },
    AssetClass.COMMODITY: {
        'energy': 1800.0, 'metals': 1800.0, 
        'agriculture': 1800.0, 'other': 1800.0
    }
}

# Supervisory Correlations
SUPERVISORY_CORRELATIONS = {
    AssetClass.INTEREST_RATE: 0.99,
    AssetClass.FOREIGN_EXCHANGE: 0.60,
    AssetClass.CREDIT: 0.50,
    AssetClass.EQUITY: 0.80,
    AssetClass.COMMODITY: 0.40
}

# Collateral Haircuts (in percentage)
COLLATERAL_HAIRCUTS = {
    CollateralType.CASH: 0.0,
    CollateralType.GOVERNMENT_BONDS: 0.5,
    CollateralType.CORPORATE_BONDS: 4.0,
    CollateralType.EQUITIES: 15.0,
    CollateralType.MONEY_MARKET: 0.5
}

# Risk Weight Mapping
RISK_WEIGHT_MAPPING = {
    'Corporate': 1.0,
    'Bank': 0.20,
    'Sovereign': 0.0,
    'Non-Profit Org': 1.0
}
