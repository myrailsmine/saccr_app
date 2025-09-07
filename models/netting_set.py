"""Netting set data models."""

from dataclasses import dataclass
from typing import List
from models.trade import Trade

@dataclass
class NettingSet:
    """Represents a netting set of trades."""
    netting_set_id: str
    counterparty: str
    trades: List[Trade]
    threshold: float = 0.0
    mta: float = 0.0
    nica: float = 0.0
    
    def total_notional(self) -> float:
        """Calculate total absolute notional."""
        return sum(abs(trade.notional) for trade in self.trades)
    
    def net_mtm(self) -> float:
        """Calculate net mark-to-market value."""
        return sum(trade.mtm_value for trade in self.trades)
    
    def is_margined(self) -> bool:
        """Check if netting set is margined."""
        return self.threshold > 0 or self.mta > 0
    
    def get_asset_classes(self) -> set:
        """Get unique asset classes in the netting set."""
        return set(trade.asset_class for trade in self.trades)
