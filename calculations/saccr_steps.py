"""Individual SA-CCR calculation step implementations."""

import math
from typing import Dict, List, Any
from datetime import datetime
from models.trade import Trade
from models.netting_set import NettingSet
from config.regulatory_params import (
    SUPERVISORY_FACTORS, SUPERVISORY_CORRELATIONS, AssetClass
)
from calculations.base_calculator import CalculationStep

class SACCRSteps:
    """Implementation of individual SA-CCR calculation steps."""
    
    @staticmethod
    def step_01_netting_set_data(netting_set: NettingSet) -> CalculationStep:
        """Step 1: Netting Set Data Collection."""
        step = CalculationStep(1, "Netting Set Data", 
                              "Source netting set data from trade repository")
        
        data = {
            'netting_set_id': netting_set.netting_set_id,
            'counterparty': netting_set.counterparty,
            'trade_count': len(netting_set.trades),
            'total_notional': netting_set.total_notional()
        }
        
        step.set_result(
            data=data,
            formula="Data sourced from system",
            result=f"Netting Set ID: {netting_set.netting_set_id}, Trades: {len(netting_set.trades)}"
        )
        
        return step
    
    @staticmethod
    def step_06_maturity_factor_enhanced(trades: List[Trade]) -> CalculationStep:
        """Step 6: Maturity Factor with dual calculation."""
        step = CalculationStep(6, "Maturity Factor (MF) - Dual Calculation",
                              "Apply Basel dual maturity factor approach")
        
        maturity_factors = []
        reasoning_details = []
        
        for trade in trades:
            remaining_maturity = trade.time_to_maturity()
            mf_margined = 0.3
            mf_unmargined = 1.0
            
            maturity_factors.append({
                'trade_id': trade.trade_id,
                'remaining_maturity': remaining_maturity,
                'maturity_factor_margined': mf_margined,
                'maturity_factor_unmargined': mf_unmargined
            })
            
            reasoning_details.append(
                f"Trade {trade.trade_id}: M={remaining_maturity:.2f}y → "
                f"MF_margined={mf_margined}, MF_unmargined={mf_unmargined}"
            )
        
        reasoning = f"""
THINKING PROCESS - DUAL CALCULATION APPROACH:
• Basel regulation requires different maturity factor treatment
• Margined MF: {mf_margined} (specific regulatory treatment)
• Unmargined MF: {mf_unmargined} (standard treatment)

DETAILED CALCULATIONS:
{chr(10).join(reasoning_details)}
        """
        
        step.set_result(
            data=maturity_factors,
            formula="MF_margined = 0.3, MF_unmargined = 1.0",
            result=f"Calculated dual maturity factors for {len(trades)} trades"
        )
        
        step.add_thinking(reasoning, 
                         f"Dual maturity factors: Margined={mf_margined}, Unmargined={mf_unmargined}")
        
        return step
    
    @staticmethod
    def get_supervisory_factor(trade: Trade) -> float:
        """Get supervisory factor in basis points."""
        if trade.asset_class == AssetClass.INTEREST_RATE:
            maturity = trade.time_to_maturity()
            currency_group = trade.currency if trade.currency in ['USD', 'EUR', 'JPY', 'GBP'] else 'other'
            
            if maturity < 2:
                return SUPERVISORY_FACTORS[AssetClass.INTEREST_RATE][currency_group]['<2y']
            elif maturity <= 5:
                return SUPERVISORY_FACTORS[AssetClass.INTEREST_RATE][currency_group]['2-5y']
            else:
                return SUPERVISORY_FACTORS[AssetClass.INTEREST_RATE][currency_group]['>5y']
        
        elif trade.asset_class == AssetClass.FOREIGN_EXCHANGE:
            from config.settings import G10_CURRENCIES
            is_g10 = trade.currency in G10_CURRENCIES
            return SUPERVISORY_FACTORS[AssetClass.FOREIGN_EXCHANGE]['G10' if is_g10 else 'emerging']
        
        elif trade.asset_class == AssetClass.CREDIT:
            return SUPERVISORY_FACTORS[AssetClass.CREDIT]['IG_single']
        
        elif trade.asset_class == AssetClass.EQUITY:
            return SUPERVISORY_FACTORS[AssetClass.EQUITY]['single_large']
        
        elif trade.asset_class == AssetClass.COMMODITY:
            return SUPERVISORY_FACTORS[AssetClass.COMMODITY]['energy']
        
        return 50.0  # Default
