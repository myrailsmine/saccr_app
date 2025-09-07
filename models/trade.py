"""Trade and financial instrument data models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from config.regulatory_params import AssetClass, TradeType

@dataclass
class Trade:
    """Represents a derivatives trade."""
    trade_id: str
    counterparty: str
    asset_class: AssetClass
    trade_type: TradeType
    notional: float
    currency: str
    underlying: str
    maturity_date: datetime
    mtm_value: float = 0.0
    delta: float = 1.0
    basis_flag: bool = False
    volatility_flag: bool = False
    ceu_flag: int = 1  # Central clearing flag
    
    def time_to_maturity(self) -> float:
        """Calculate time to maturity in years."""
        return max(0, (self.maturity_date - datetime.now()).days / 365.25)
    
    def is_option_like(self) -> bool:
        """Check if trade is option-like."""
        return self.trade_type in [TradeType.OPTION, TradeType.SWAPTION]
    
    def effective_delta(self) -> float:
        """Get effective delta for calculations."""
        if self.is_option_like():
            return self.delta
        return 1.0 if self.notional > 0 else -1.0
