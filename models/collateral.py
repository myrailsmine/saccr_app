# models/collateral.py
"""Collateral data model."""

from dataclasses import dataclass
from models.enums import CollateralType

@dataclass
class Collateral:
    """Represents collateral with effective value calculation."""
    collateral_type: CollateralType
    currency: str
    amount: float
    haircut: float = 0.0
    
    def effective_value(self) -> float:
        """Calculate effective value after haircut."""
        return self.amount * (1 - self.haircut / 100)
