# models/enums.py
"""Enumerations for asset classes, trade types, and other classifications."""

from enum import Enum

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

class DataQualityIssueType(Enum):
    MISSING = "missing"
    ESTIMATED = "estimated"
    OUTDATED = "outdated"

class DataQualityImpact(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
