# calculations/validation.py
"""Input validation for SA-CCR calculations."""

from typing import Dict, List, Any
from models.netting_set import NettingSet
from models.collateral import Collateral
from models.enums import TradeType

class SACCRValidator:
    """Validator for SA-CCR calculation inputs."""
    
    def validate_input_completeness(self, netting_set: NettingSet, 
                                   collateral: List[Collateral] = None) -> Dict[str, Any]:
        """Validate if all required inputs are provided."""
        missing_fields = []
        warnings = []
        
        # Validate netting set
        if not netting_set.netting_set_id:
            missing_fields.append("Netting Set ID")
        if not netting_set.counterparty:
            missing_fields.append("Counterparty name")
        if not netting_set.trades:
            missing_fields.append("At least one trade")
        
        # Validate trades
        for i, trade in enumerate(netting_set.trades):
            trade_prefix = f"Trade {i+1}"
            
            if not trade.trade_id:
                missing_fields.append(f"{trade_prefix}: Trade ID")
            if not trade.notional or trade.notional == 0:
                missing_fields.append(f"{trade_prefix}: Notional amount")
            if not trade.currency:
                missing_fields.append(f"{trade_prefix}: Currency")
            if not trade.maturity_date:
                missing_fields.append(f"{trade_prefix}: Maturity date")
            
            # Option-specific validations
            if trade.trade_type in [TradeType.OPTION, TradeType.SWAPTION]:
                if trade.delta == 1.0:
                    warnings.append(f"{trade_prefix}: Delta not specified for option (using default 1.0)")
        
        return {
            'is_complete': len(missing_fields) == 0,
            'missing_fields': missing_fields,
            'warnings': warnings,
            'can_proceed': len(missing_fields) == 0
        }
