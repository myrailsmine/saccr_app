"""Netting set data model with aggregation methods."""

from dataclasses import dataclass
from typing import List, Set, Dict
from models.trade import Trade
from models.enums import AssetClass

@dataclass
class NettingSet:
    """Represents a netting set of trades with aggregation methods."""
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
    
    def get_asset_classes(self) -> Set[AssetClass]:
        """Get unique asset classes in the netting set."""
        return set(trade.asset_class for trade in self.trades)
    
    def get_currencies(self) -> Set[str]:
        """Get unique currencies in the netting set."""
        return set(trade.currency for trade in self.trades)
    
    def get_hedging_sets(self) -> Dict[str, List[Trade]]:
        """Group trades into hedging sets."""
        hedging_sets = {}
        for trade in self.trades:
            key = f"{trade.asset_class.value}_{trade.currency}"
            if key not in hedging_sets:
                hedging_sets[key] = []
            hedging_sets[key].append(trade)
        return hedging_sets
