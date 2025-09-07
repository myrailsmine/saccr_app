# calculations/enhanced_analytics.py
"""Enhanced analytics and summary generation."""

from typing import Dict, List, Any
from models.netting_set import NettingSet
from calculations.base_calculator import CalculationStep

class EnhancedAnalytics:
    """Enhanced analytics for SA-CCR calculations."""
    
    def generate_enhanced_summary(self, calculation_steps: List[CalculationStep], 
                                 netting_set: NettingSet) -> Dict[str, List[str]]:
        """Generate enhanced bulleted summary."""
        
        final_step_21 = next(step for step in calculation_steps if step.step == 21)
        final_step_24 = next(step for step in calculation_steps if step.step == 24)
        final_step_16 = next(step for step in calculation_steps if step.step == 16)
        final_step_18 = next(step for step in calculation_steps if step.step == 18)
        final_step_15 = next(step for step in calculation_steps if step.step == 15)
        final_step_13 = next(step for step in calculation_steps if step.step == 13)
        
        total_notional = sum(abs(trade.notional) for trade in netting_set.trades)
        
        return {
            'key_inputs': [
                f"Portfolio: {len(netting_set.trades)} trades totaling ${total_notional:,.0f} notional",
                f"Counterparty: {netting_set.counterparty}",
                f"Netting arrangement: {'Margined' if netting_set.is_margined() else 'Unmargined'} set",
                f"Asset classes: {', '.join(ac.value for ac in netting_set.get_asset_classes())}"
            ],
            'risk_components': [
                f"Aggregate Add-On: ${final_step_13.data.get('aggregate_addon', 0):,.0f}",
                f"PFE Multiplier: {final_step_15.data.get('multiplier', 1.0):.4f} ({(1-final_step_15.data.get('multiplier', 1.0))*100:.1f}% netting benefit)",
                f"Potential Future Exposure: ${final_step_16.data.get('pfe', 0):,.0f}",
                f"Replacement Cost: ${final_step_18.data.get('rc', 0):,.0f}",
            ],
            'capital_results': [
                f"Exposure at Default (EAD): ${final_step_21.data.get('ead', 0):,.0f}",
                f"Risk Weight: {final_step_24.data.get('risk_weight_pct', 100):.0f}%",
                f"Risk-Weighted Assets: ${final_step_24.data.get('rwa', 0):,.0f}",
                f"Minimum Capital Required: ${final_step_24.data.get('capital_requirement', 0):,.0f}",
                f"Capital Efficiency: {(final_step_24.data.get('capital_requirement', 0)/total_notional*100 if total_notional > 0 else 0):.3f}% of notional"
            ],
            'optimization_insights': [
                f"Netting benefits reduce PFE by {(1-final_step_15.data.get('multiplier', 1.0))*100:.1f}%",
                f"Portfolio shows {'strong' if final_step_15.data.get('multiplier', 1.0) < 0.5 else 'moderate' if final_step_15.data.get('multiplier', 1.0) < 0.8 else 'limited'} netting efficiency"
            ]
        }
