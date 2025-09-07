# config/regulatory_params.py
"""Basel SA-CCR regulatory parameters and supervisory factors."""

from typing import Dict
from models.enums import AssetClass, CollateralType


# Corrected Regulatory Parameters (matching enterprise app)
SUPERVISORY_FACTORS = {
    AssetClass.INTEREST_RATE: {
        'USD': {'<2y': 0.50, '2-5y': 0.50, '>5y': 1.50},
        'EUR': {'<2y': 0.50, '2-5y': 0.50, '>5y': 1.50},
        'JPY': {'<2y': 0.50, '2-5y': 0.50, '>5y': 1.50},
        'GBP': {'<2y': 0.50, '2-5y': 0.50, '>5y': 1.50},
        'other': {'<2y': 1.50, '2-5y': 1.50, '>5y': 1.50}
    },
    AssetClass.FOREIGN_EXCHANGE: {'G10': 4.0, 'emerging': 15.0},
    AssetClass.CREDIT: {
        'IG_single': 0.46, 'HY_single': 1.30,
        'IG_index': 0.38, 'HY_index': 1.06
    },
    AssetClass.EQUITY: {
        'single_large': 32.0, 'single_small': 40.0,
        'index_developed': 20.0, 'index_emerging': 25.0
    },
    AssetClass.COMMODITY: {
        'energy': 18.0, 'metals': 18.0, 
        'agriculture': 18.0, 'other': 18.0
    }
}

SUPERVISORY_CORRELATIONS = {
    AssetClass.INTEREST_RATE: 0.99,
    AssetClass.FOREIGN_EXCHANGE: 0.60,
    AssetClass.CREDIT: 0.50,
    AssetClass.EQUITY: 0.80,
    AssetClass.COMMODITY: 0.40
}

COLLATERAL_HAIRCUTS = {
    CollateralType.CASH: 0.0,
    CollateralType.GOVERNMENT_BONDS: 0.5,
    CollateralType.CORPORATE_BONDS: 4.0,
    CollateralType.EQUITIES: 15.0,
    CollateralType.MONEY_MARKET: 0.5
}

RISK_WEIGHT_MAPPING = {
    'Corporate': 1.0,
    'Bank': 0.20,
    'Sovereign': 0.0,
    'Non-Profit Org': 1.0
}

G10_CURRENCIES = ['USD', 'EUR', 'JPY', 'GBP', 'CHF', 'CAD', 'AUD', 'NZD', 'SEK', 'NOK']
BASEL_ALPHA = 1.4
BASEL_CAPITAL_RATIO = 0.08
