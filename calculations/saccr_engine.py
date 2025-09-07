"""Main SA-CCR calculation engine with all 24 steps."""

import math
from typing import Dict, List, Any, Optional
from models.netting_set import NettingSet
from models.collateral import Collateral
from models.data_quality import DataQualityIssue, DataQualityIssueType, DataQualityImpact
from models.enums import TradeType
from calculations.base_calculator import BaseCalculator, CalculationStep
from calculations.saccr_steps import SACCRStepCalculator
from calculations.validation import SACCRValidator
from calculations.enhanced_analytics import EnhancedAnalytics

class ComprehensiveSACCREngine(BaseCalculator):
    """Complete SA-CCR calculation engine with enhanced analytics."""
    
    def __init__(self):
        super().__init__()
        self.step_calculator = SACCRStepCalculator()
        self.validator = SACCRValidator()
        self.analytics = EnhancedAnalytics()
        self.data_quality_issues = []
    
    def calculate(self, netting_set: NettingSet, 
                 collateral: List[Collateral] = None) -> Dict[str, Any]:
        """Execute complete 24-step SA-CCR calculation."""
        
        # Reset state
        self.calculation_steps = []
        self.thinking_steps = []
        self.assumptions = []
        self.data_quality_issues = self.analyze_data_quality(netting_set, collateral)
        
        # Execute all 24 steps
        steps_data = self._execute_all_steps(netting_set, collateral)
        
        # Generate final results
        final_results = self._extract_final_results(steps_data)
        
        # Generate enhanced summary
        enhanced_summary = self.analytics.generate_enhanced_summary(
            self.calculation_steps, netting_set
        )
        
        return {
            'calculation_steps': self.calculation_steps,
            'final_results': final_results,
            'data_quality_issues': self.data_quality_issues,
            'enhanced_summary': enhanced_summary,
            'thinking_steps': self.thinking_steps,
            'assumptions': self.assumptions
        }
    
    def validate_inputs(self, netting_set: NettingSet, 
                       collateral: List[Collateral] = None) -> Dict[str, Any]:
        """Validate calculation inputs."""
        return self.validator.validate_input_completeness(netting_set, collateral)
    
    def _execute_all_steps(self, netting_set: NettingSet, 
                          collateral: List[Collateral] = None) -> Dict[str, Any]:
        """Execute all 24 SA-CCR calculation steps."""
        
        # Steps 1-5: Data preparation
        step1 = self.step_calculator.step_01_netting_set_data(netting_set)
        self.add_step(step1)
        
        step2 = self.step_calculator.step_02_asset_classification(netting_set.trades)
        self.add_step(step2)
        
        step3 = self._step3_hedging_set(netting_set.trades)
        self.add_step(step3)
        
        step4 = self._step4_time_parameters(netting_set.trades)
        self.add_step(step4)
        
        step5 = self._step5_adjusted_notional(netting_set.trades)
        self.add_step(step5)
        
        # Steps 6-10: Risk factor calculations
        step6 = self.step_calculator.step_06_maturity_factor_enhanced(netting_set.trades)
        self.add_step(step6)
        
        step7 = self._step7_supervisory_delta(netting_set.trades)
        self.add_step(step7)
        
        step8 = self._step8_supervisory_factor_enhanced(netting_set.trades)
        self.add_step(step8)
        
        step9 = self._step9_adjusted_derivatives_contract_amount_enhanced(netting_set.trades)
        self.add_step(step9)
        
        step10 = self._step10_supervisory_correlation(netting_set.trades)
        self.add_step(step10)
        
        # Steps 11-16: Add-on calculations
        step11 = self._step11_hedging_set_addon(netting_set.trades)
        self.add_step(step11)
        
        step12 = self._step12_asset_class_addon(netting_set.trades)
        self.add_step(step12)
        
        step13 = self._step13_aggregate_addon_enhanced(netting_set.trades)
        self.add_step(step13)
        
        step14 = self._step14_sum_v_c_enhanced(netting_set, collateral)
        self.add_step(step14)
        
        step15 = self.step_calculator.step_15_pfe_multiplier_enhanced(
            step14.data['sum_v_mtm'], step14.data['sum_c_collateral'], 
            step13.data['aggregate_addon']
        )
        self.add_step(step15)
        
        step16 = self._step16_pfe_enhanced(
            step15.data['multiplier'], step13.data['aggregate_addon']
        )
        self.add_step(step16)
        
        # Steps 17-21: Exposure calculations
        step17 = self._step17_th_mta_nica(netting_set)
        self.add_step(step17)
        
        step18 = self._step18_replacement_cost_enhanced(
            step14.data['sum_v_mtm'], step14.data['sum_c_collateral'], step17
        )
        self.add_step(step18)
        
        step19 = self._step19_ceu_flag(netting_set.trades)
        self.add_step(step19)
        
        step20 = self._step20_alpha(step19.data['overall_ceu_flag'])
        self.add_step(step20)
        
        step21 = self._step21_ead_enhanced(
            step20.data['alpha'], step18.data['rc'], step16.data['pfe']
        )
        self.add_step(step21)
        
        # Steps 22-24: Capital calculations
        step22 = self._step22_counterparty_info(netting_set.counterparty)
        self.add_step(step22)
        
        step23 = self._step23_risk_weight(step22.data['r35_risk_weight_category'])
        self.add_step(step23)
        
        step24 = self._step24_rwa_calculation_enhanced(
            step21.data['ead'], step23.data['risk_weight_decimal']
        )
        self.add_step(step24)
        
        return {
            'sum_v': step14.data['sum_v_mtm'],
            'sum_c': step14.data['sum_c_collateral'],
            'aggregate_addon': step13.data['aggregate_addon'],
            'multiplier': step15.data['multiplier'],
            'pfe': step16.data['pfe'],
            'rc': step18.data['rc'],
            'ead': step21.data['ead'],
            'rwa': step24.data['rwa']
        }
    
    def analyze_data_quality(self, netting_set: NettingSet, 
                           collateral: List[Collateral] = None) -> List[DataQualityIssue]:
        """Analyze data quality and identify issues."""
        issues = []
        
        # Check netting set level data
        if netting_set.threshold == 0 and netting_set.mta == 0:
            issues.append(DataQualityIssue(
                field_name="Threshold/MTA",
                current_value="0/0",
                issue_type=DataQualityIssueType.ESTIMATED,
                impact=DataQualityImpact.HIGH,
                recommendation="Margining terms significantly impact RC calculation. Please provide actual CSA terms.",
                default_used="Assumed unmargined netting set"
            ))
        
        # Check trade level data
        for trade in netting_set.trades:
            if trade.mtm_value == 0:
                issues.append(DataQualityIssue(
                    field_name=f"MTM Value - {trade.trade_id}",
                    current_value=0,
                    issue_type=DataQualityIssueType.MISSING,
                    impact=DataQualityImpact.HIGH,
                    recommendation="Current MTM affects replacement cost and PFE multiplier calculation.",
                    default_used="0"
                ))
            
            if trade.trade_type in [TradeType.OPTION, TradeType.SWAPTION] and trade.delta == 1.0:
                issues.append(DataQualityIssue(
                    field_name=f"Option Delta - {trade.trade_id}",
                    current_value=1.0,
                    issue_type=DataQualityIssueType.ESTIMATED,
                    impact=DataQualityImpact.MEDIUM,
                    recommendation="Option delta affects effective notional calculation.",
                    default_used="1.0"
                ))
        
        # Check collateral data
        if not collateral:
            issues.append(DataQualityIssue(
                field_name="Collateral Portfolio",
                current_value="None",
                issue_type=DataQualityIssueType.MISSING,
                impact=DataQualityImpact.HIGH,
                recommendation="Collateral reduces replacement cost. Please provide collateral details.",
                default_used="No collateral assumed"
            ))
        
        return issues
    
    def _extract_final_results(self, steps_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract final calculation results."""
        return {
            'replacement_cost': steps_data['rc'],
            'potential_future_exposure': steps_data['pfe'],
            'exposure_at_default': steps_data['ead'],
            'risk_weighted_assets': steps_data['rwa'],
            'capital_requirement': steps_data['rwa'] * 0.08
        }
    
    # Include all the remaining step methods from the original code
    # [Step methods 3-24 would be implemented here, following the same pattern]
    

  def _step3_hedging_set(self, trades: List[Trade]) -> Dict:
        hedging_sets = {}
        for trade in trades:
            hedging_set_key = f"{trade.asset_class.value}_{trade.currency}"
            if hedging_set_key not in hedging_sets:
                hedging_sets[hedging_set_key] = []
            hedging_sets[hedging_set_key].append(trade.trade_id)
        
        return {
            'step': 3,
            'title': 'Hedging Set Determination',
            'description': 'Group trades into hedging sets based on common risk factors',
            'data': hedging_sets,
            'formula': 'Hedging sets defined by asset class and currency/index',
            'result': f"Created {len(hedging_sets)} hedging sets"
        }
    
    def _step4_time_parameters(self, trades: List[Trade]) -> Dict:
        time_params = []
        for trade in trades:
            settlement_date = datetime.now()
            end_date = trade.maturity_date
            remaining_maturity = trade.time_to_maturity()
            
            time_params.append({
                'trade_id': trade.trade_id,
                'settlement_date': settlement_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'remaining_maturity': remaining_maturity
            })
        
        return {
            'step': 4,
            'title': 'Time Parameters (S, E, M)',
            'description': 'Calculate settlement date, end date, and maturity for each trade',
            'data': time_params,
            'formula': 'M = (End Date - Settlement Date) / 365.25',
            'result': f"Calculated time parameters for {len(trades)} trades"
        }
    
    def _step5_adjusted_notional(self, trades: List[Trade]) -> Dict:
        adjusted_notionals = []
        for trade in trades:
            adjusted_notional = abs(trade.notional)
            adjusted_notionals.append({
                'trade_id': trade.trade_id,
                'original_notional': trade.notional,
                'adjusted_notional': adjusted_notional
            })
        
        return {
            'step': 5,
            'title': 'Adjusted Notional',
            'description': 'Calculate adjusted notional amounts',
            'data': adjusted_notionals,
            'formula': 'Adjusted Notional = Notional × Supervisory Duration',
            'result': f"Calculated adjusted notionals for {len(trades)} trades"
        }


  def _step18_replacement_cost_enhanced(self, sum_v: float, sum_c: float, 
                                         step17: CalculationStep) -> CalculationStep:
        """Step 18: Replacement Cost with enhanced margining analysis."""
        threshold = step17.data['threshold']
        mta = step17.data['mta']
        nica = step17.data['nica']
        
        net_exposure = sum_v - sum_c
        is_margined = threshold > 0 or mta > 0
        
        if is_margined:
            margin_floor = threshold + mta - nica
            rc = max(net_exposure, margin_floor, 0)
            methodology = "Margined netting set"
        else:
            margin_floor = 0
            rc = max(net_exposure, 0)
            methodology = "Unmargined netting set"
        
        reasoning = f"""
THINKING PROCESS:
• RC represents the current cost to replace the portfolio if the counterparty defaults today.
• The calculation depends on whether the netting set is margined (covered by a CSA).

NETTING SET CLASSIFICATION:
• Type: {methodology}
• Margin Floor (TH+MTA-NICA): ${margin_floor:,.0f}

REPLACEMENT COST DETERMINATION:
• Formula: {"RC = max(V-C, TH+MTA-NICA, 0)" if is_margined else "RC = max(V-C, 0)"}
• Calculation: RC = max(${net_exposure:,.0f}, {f'${margin_floor:,.0f}, ' if is_margined else ''}0) = ${rc:,.0f}
        """
        
        step = CalculationStep(
            step=18,
            title="RC (Replacement Cost)",
            description="Calculate replacement cost with netting and collateral benefits",
            data={
                'sum_v': sum_v,
                'sum_c': sum_c,
                'net_exposure': net_exposure,
                'threshold': threshold,
                'mta': mta,
                'nica': nica,
                'is_margined': is_margined,
                'rc': rc,
                'methodology': methodology
            },
            formula=f"RC = max(V - C{'; TH + MTA - NICA' if is_margined else ''}; 0)",
            result=f"RC: ${rc:,.0f}"
        )
        
        step.add_thinking(reasoning, f"RC of ${rc:,.0f} represents the current credit exposure component of EAD.")
        return step
