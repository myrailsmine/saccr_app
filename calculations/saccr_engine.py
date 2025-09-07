# ==============================================================================
# ENHANCED SA-CCR ENGINE - MARGINED/UNMARGINED SCENARIOS
# ==============================================================================

"""
Enhanced SA-CCR calculation engine that computes both margined and unmargined 
scenarios and selects the minimum EAD as per Basel requirements.
"""

import math
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# ==============================================================================
# ENUMS AND DATA CLASSES
# ==============================================================================

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

@dataclass
class Trade:
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
    ceu_flag: int = 1
    
    def time_to_maturity(self) -> float:
        return max(0, (self.maturity_date - datetime.now()).days / 365.25)

@dataclass
class NettingSet:
    netting_set_id: str
    counterparty: str
    trades: List[Trade]
    threshold: float = 0.0
    mta: float = 0.0
    nica: float = 0.0

@dataclass
class Collateral:
    collateral_type: CollateralType
    currency: str
    amount: float
    haircut: float = 0.0

# ==============================================================================
# REGULATORY PARAMETERS
# ==============================================================================

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

# ==============================================================================
# ENHANCED SA-CCR ENGINE WITH DUAL SCENARIOS
# ==============================================================================

class UnifiedSACCREngine:
    """
    Enhanced SA-CCR engine that computes both margined and unmargined scenarios
    and selects the minimum EAD as per Basel regulatory requirements.
    """
    
    def __init__(self):
        """Initialize the enhanced SA-CCR engine."""
        self.supervisory_factors = SUPERVISORY_FACTORS
        self.supervisory_correlations = SUPERVISORY_CORRELATIONS
        self.collateral_haircuts = COLLATERAL_HAIRCUTS
        self.risk_weight_mapping = RISK_WEIGHT_MAPPING
        
        # Calculation state
        self.calculation_steps: List[Dict] = []
        self.thinking_steps: List[Dict[str, Any]] = []
        self.assumptions: List[str] = []
    
    def calculate_dual_scenario_saccr(self, netting_set: NettingSet, 
                                     collateral: List[Collateral] = None) -> Dict[str, Any]:
        """
        Calculate SA-CCR for both margined and unmargined scenarios and select minimum EAD.
        
        This follows Basel regulatory requirement to compute both scenarios and use
        the approach that yields the lower capital requirement.
        """
        print("🔄 Computing SA-CCR for both margined and unmargined scenarios...")
        
        # Scenario 1: Margined (using provided CSA terms)
        print("📊 Calculating Scenario 1: Margined netting set")
        margined_results = self._calculate_single_scenario(
            netting_set=netting_set,
            collateral=collateral,
            force_margined=True,
            scenario_name="Margined"
        )
        
        # Scenario 2: Unmargined (ignoring CSA terms)
        print("📊 Calculating Scenario 2: Unmargined netting set")
        unmargined_netting_set = NettingSet(
            netting_set_id=netting_set.netting_set_id + "_UNMARGINED",
            counterparty=netting_set.counterparty,
            trades=netting_set.trades,
            threshold=0.0,  # Force unmargined
            mta=0.0,
            nica=0.0
        )
        
        unmargined_results = self._calculate_single_scenario(
            netting_set=unmargined_netting_set,
            collateral=None,  # No collateral benefit in unmargined scenario
            force_margined=False,
            scenario_name="Unmargined"
        )
        
        # Compare and select minimum EAD scenario
        margined_ead = margined_results['final_results']['exposure_at_default']
        unmargined_ead = unmargined_results['final_results']['exposure_at_default']
        
        selected_scenario = "Margined" if margined_ead <= unmargined_ead else "Unmargined"
        selected_results = margined_results if margined_ead <= unmargined_ead else unmargined_results
        
        print(f"✅ Selected scenario: {selected_scenario} (EAD: ${margined_ead if selected_scenario == 'Margined' else unmargined_ead:,.0f})")
        
        # Create comprehensive dual scenario results
        dual_results = {
            'scenarios': {
                'margined': {
                    'results': margined_results,
                    'ead': margined_ead,
                    'rc': margined_results['final_results']['replacement_cost'],
                    'pfe': margined_results['final_results']['potential_future_exposure'],
                    'rwa': margined_results['final_results']['risk_weighted_assets'],
                    'capital': margined_results['final_results']['capital_requirement']
                },
                'unmargined': {
                    'results': unmargined_results,
                    'ead': unmargined_ead,
                    'rc': unmargined_results['final_results']['replacement_cost'],
                    'pfe': unmargined_results['final_results']['potential_future_exposure'],
                    'rwa': unmargined_results['final_results']['risk_weighted_assets'],
                    'capital': unmargined_results['final_results']['capital_requirement']
                }
            },
            'selection': {
                'selected_scenario': selected_scenario,
                'selection_rationale': f"Selected {selected_scenario.lower()} scenario with EAD of ${margined_ead if selected_scenario == 'Margined' else unmargined_ead:,.0f} as it yields lower capital requirement",
                'ead_difference': abs(margined_ead - unmargined_ead),
                'capital_savings': abs(margined_results['final_results']['capital_requirement'] - 
                                     unmargined_results['final_results']['capital_requirement'])
            },
            'final_results': selected_results['final_results'],
            'selected_calculation_steps': selected_results['calculation_steps'],
            'comparison_summary': self._generate_comparison_summary(margined_results, unmargined_results, selected_scenario)
        }
        
        return dual_results
    
    def _calculate_single_scenario(self, netting_set: NettingSet, 
                                  collateral: List[Collateral] = None,
                                  force_margined: bool = True,
                                  scenario_name: str = "") -> Dict[str, Any]:
        """Calculate SA-CCR for a single scenario (margined or unmargined)."""
        
        # Reset calculation state
        self.calculation_steps = []
        self.thinking_steps = []
        self.assumptions = []
        
        # Add scenario tracking
        if scenario_name:
            self.assumptions.append(f"Scenario: {scenario_name} calculation")
        
        # Execute calculation steps (same as before, but with scenario tracking)
        calculation_steps = []
        
        # Steps 1-13: PFE calculation (same for both scenarios)
        for step_num in range(1, 14):
            step_data = self._execute_step(step_num, netting_set, collateral)
            calculation_steps.append(step_data)
        
        # Get aggregate addon for PFE calculations
        aggregate_addon = calculation_steps[12]['aggregate_addon']  # Step 13
        
        # Step 14: Sum of V, C
        step14_data = self._step14_sum_v_c_enhanced(netting_set, collateral, scenario_name)
        calculation_steps.append(step14_data)
        sum_v = step14_data['sum_v']
        sum_c = step14_data['sum_c']

        # Step 15: PFE Multiplier
        step15_data = self._step15_pfe_multiplier_enhanced(sum_v, sum_c, aggregate_addon, scenario_name)
        calculation_steps.append(step15_data)
        
        # Step 16: PFE
        step16_data = self._step16_pfe_enhanced(step15_data['multiplier'], aggregate_addon, scenario_name)
        calculation_steps.append(step16_data)
        
        # Step 17: TH, MTA, NICA
        step17_data = self._step17_th_mta_nica(netting_set, scenario_name)
        calculation_steps.append(step17_data)
        
        # Step 18: RC (scenario-specific)
        step18_data = self._step18_replacement_cost_enhanced(sum_v, sum_c, step17_data, scenario_name)
        calculation_steps.append(step18_data)
        
        # Steps 19-24: Final EAD and RWA calculation
        for step_num in range(19, 25):
            if step_num == 21:
                step_data = self._step21_ead_enhanced(
                    BASEL_ALPHA, step18_data['rc'], step16_data['pfe'], scenario_name
                )
            elif step_num == 24:
                step23_data = calculation_steps[22]  # Risk weight from step 23
                step_data = self._step24_rwa_calculation_enhanced(
                    calculation_steps[20]['ead'], step23_data['risk_weight'], scenario_name
                )
            else:
                step_data = self._execute_step(step_num, netting_set, collateral, scenario_name)
            calculation_steps.append(step_data)
        
        # Store and return results
        self.calculation_steps = calculation_steps
        
        return {
            'calculation_steps': calculation_steps,
            'final_results': {
                'replacement_cost': step18_data['rc'],
                'potential_future_exposure': step16_data['pfe'],
                'exposure_at_default': calculation_steps[20]['ead'],  # Step 21
                'risk_weighted_assets': calculation_steps[23]['rwa'],  # Step 24
                'capital_requirement': calculation_steps[23]['rwa'] * BASEL_CAPITAL_RATIO
            },
            'scenario_name': scenario_name,
            'thinking_steps': self.thinking_steps,
            'assumptions': self.assumptions
        }
    
    def _execute_step(self, step_num: int, netting_set: NettingSet, 
                     collateral: List[Collateral] = None, scenario_name: str = "") -> Dict:
        """Execute a specific calculation step."""
        
        if step_num == 1:
            return self._step1_netting_set_data(netting_set)
        elif step_num == 2:
            return self._step2_asset_classification(netting_set.trades)
        elif step_num == 3:
            return self._step3_hedging_set(netting_set.trades)
        elif step_num == 4:
            return self._step4_time_parameters(netting_set.trades)
        elif step_num == 5:
            return self._step5_adjusted_notional(netting_set.trades)
        elif step_num == 6:
            return self._step6_maturity_factor_enhanced(netting_set.trades)
        elif step_num == 7:
            return self._step7_supervisory_delta(netting_set.trades)
        elif step_num == 8:
            return self._step8_supervisory_factor_enhanced(netting_set.trades)
        elif step_num == 9:
            return self._step9_adjusted_derivatives_contract_amount_enhanced(netting_set.trades)
        elif step_num == 10:
            return self._step10_supervisory_correlation(netting_set.trades)
        elif step_num == 11:
            return self._step11_hedging_set_addon(netting_set.trades)
        elif step_num == 12:
            return self._step12_asset_class_addon(netting_set.trades)
        elif step_num == 13:
            return self._step13_aggregate_addon_enhanced(netting_set.trades)
        elif step_num == 19:
            return self._step19_ceu_flag(netting_set.trades)
        elif step_num == 20:
            return self._step20_alpha(1)  # Default CEU flag
        elif step_num == 22:
            return self._step22_counterparty_info(netting_set.counterparty)
        elif step_num == 23:
            return self._step23_risk_weight("Corporate")  # Default
        else:
            return {"step": step_num, "error": "Step not implemented"}
    
    # ==============================================================================
    # ENHANCED STEP IMPLEMENTATIONS WITH SCENARIO TRACKING
    # ==============================================================================
    
    def _step14_sum_v_c_enhanced(self, netting_set: NettingSet, 
                                collateral: List[Collateral] = None,
                                scenario_name: str = "") -> Dict:
        """Step 14: V and C calculation with scenario awareness."""
        sum_v = sum(trade.mtm_value for trade in netting_set.trades)
        
        sum_c = 0
        collateral_details = []
        
        # In unmargined scenario, ignore collateral benefits
        if scenario_name == "Unmargined":
            sum_c = 0
            self.assumptions.append(f"{scenario_name}: Collateral benefits ignored in unmargined scenario")
        elif collateral:
            for coll in collateral:
                haircut = self.collateral_haircuts.get(coll.collateral_type, 15.0) / 100
                effective_value = coll.amount * (1 - haircut)
                sum_c += effective_value
                
                collateral_details.append({
                    'type': coll.collateral_type.value,
                    'amount': coll.amount,
                    'haircut_pct': haircut * 100,
                    'effective_value': effective_value
                })
        else:
            self.assumptions.append(f"{scenario_name}: No collateral provided")
        
        return {
            'step': 14,
            'title': f'Sum of V, C within netting set ({scenario_name})',
            'description': f'Calculate sum of MTM values and effective collateral - {scenario_name} scenario',
            'data': {
                'sum_v_mtm': sum_v,
                'sum_c_collateral': sum_c,
                'net_exposure': sum_v - sum_c,
                'collateral_details': collateral_details,
                'scenario': scenario_name
            },
            'formula': 'V = Σ(MTM values), C = Σ(Collateral × (1 - haircut))',
            'result': f"Sum V: ${sum_v:,.0f}, Sum C: ${sum_c:,.0f} ({scenario_name})",
            'sum_v': sum_v,
            'sum_c': sum_c
        }
    
    def _step18_replacement_cost_enhanced(self, sum_v: float, sum_c: float, 
                                         step17_data: Dict, scenario_name: str = "") -> Dict:
        """Step 18: RC calculation with scenario-specific logic."""
        threshold = step17_data['threshold']
        mta = step17_data['mta']
        nica = step17_data['nica']
        
        net_exposure = sum_v - sum_c
        
        # Scenario-specific RC calculation
        if scenario_name == "Unmargined" or (threshold == 0 and mta == 0):
            # Unmargined formula
            rc = max(net_exposure, 0)
            methodology = f"Unmargined netting set ({scenario_name})"
            margin_floor = 0
        else:
            # Margined formula
            margin_floor = threshold + mta - nica
            rc = max(net_exposure, margin_floor, 0)
            methodology = f"Margined netting set ({scenario_name})"
        
        return {
            'step': 18,
            'title': f'RC (Replacement Cost) - {scenario_name}',
            'description': f'Calculate replacement cost - {scenario_name} scenario',
            'data': {
                'sum_v': sum_v,
                'sum_c': sum_c,
                'net_exposure': net_exposure,
                'threshold': threshold,
                'mta': mta,
                'nica': nica,
                'rc': rc,
                'methodology': methodology,
                'scenario': scenario_name,
                'margin_floor': margin_floor
            },
            'formula': f"RC = max(V - C{'; TH + MTA - NICA' if scenario_name == 'Margined' else ''}; 0)",
            'result': f"RC: ${rc:,.0f} ({scenario_name})",
            'rc': rc
        }
    
    # Additional enhanced methods with scenario tracking...
    def _step15_pfe_multiplier_enhanced(self, sum_v: float, sum_c: float, 
                                       aggregate_addon: float, scenario_name: str = "") -> Dict:
        """Step 15: PFE Multiplier with scenario tracking."""
        net_exposure = sum_v - sum_c
        
        if aggregate_addon > 0:
            exponent = net_exposure / (2 * 0.95 * aggregate_addon)
            multiplier = min(1.0, 0.05 + 0.95 * math.exp(exponent))
        else:
            multiplier = 1.0
            exponent = 0
        
        return {
            'step': 15,
            'title': f'PFE Multiplier ({scenario_name})',
            'description': f'Calculate PFE multiplier - {scenario_name} scenario',
            'data': {
                'sum_v': sum_v,
                'sum_c': sum_c,
                'net_exposure': net_exposure,
                'aggregate_addon': aggregate_addon,
                'exponent': exponent,
                'multiplier': multiplier,
                'scenario': scenario_name
            },
            'formula': 'Multiplier = min(1, 0.05 + 0.95 × exp((V-C) / (1.9 × AddOn)))',
            'result': f"PFE Multiplier: {multiplier:.6f} ({scenario_name})",
            'multiplier': multiplier
        }
    
    def _step16_pfe_enhanced(self, multiplier: float, aggregate_addon: float, 
                            scenario_name: str = "") -> Dict:
        """Step 16: PFE calculation with scenario tracking."""
        pfe = multiplier * aggregate_addon
        
        return {
            'step': 16,
            'title': f'PFE (Potential Future Exposure) - {scenario_name}',
            'description': f'Calculate PFE - {scenario_name} scenario',
            'data': {
                'multiplier': multiplier,
                'aggregate_addon': aggregate_addon,
                'pfe': pfe,
                'scenario': scenario_name
            },
            'formula': 'PFE = Multiplier × Aggregate AddOn',
            'result': f"PFE: ${pfe:,.0f} ({scenario_name})",
            'pfe': pfe
        }
    
    def _step17_th_mta_nica(self, netting_set: NettingSet, scenario_name: str = "") -> Dict:
        """Step 17: TH, MTA, NICA with scenario awareness."""
        return {
            'step': 17,
            'title': f'TH, MTA, NICA ({scenario_name})',
            'description': f'Extract CSA terms - {scenario_name} scenario',
            'data': {
                'threshold': netting_set.threshold,
                'mta': netting_set.mta,
                'nica': netting_set.nica,
                'scenario': scenario_name
            },
            'formula': 'Sourced from CSA/ISDA agreements',
            'result': f"TH: ${netting_set.threshold:,.0f}, MTA: ${netting_set.mta:,.0f}, NICA: ${netting_set.nica:,.0f} ({scenario_name})",
            'threshold': netting_set.threshold,
            'mta': netting_set.mta,
            'nica': netting_set.nica
        }
    
    def _step21_ead_enhanced(self, alpha: float, rc: float, pfe: float, 
                            scenario_name: str = "") -> Dict:
        """Step 21: EAD calculation with scenario tracking."""
        combined_exposure = rc + pfe
        ead = alpha * combined_exposure
        
        return {
            'step': 21,
            'title': f'EAD (Exposure at Default) - {scenario_name}',
            'description': f'Calculate final EAD - {scenario_name} scenario',
            'data': {
                'alpha': alpha,
                'rc': rc,
                'pfe': pfe,
                'combined_exposure': combined_exposure,
                'ead': ead,
                'scenario': scenario_name
            },
            'formula': 'EAD = Alpha × (RC + PFE)',
            'result': f"EAD: ${ead:,.0f} ({scenario_name})",
            'ead': ead
        }
    
    def _step24_rwa_calculation_enhanced(self, ead: float, risk_weight: float, 
                                       scenario_name: str = "") -> Dict:
        """Step 24: RWA calculation with scenario tracking."""
        rwa = ead * risk_weight
        capital_requirement = rwa * BASEL_CAPITAL_RATIO
        
        return {
            'step': 24,
            'title': f'RWA Calculation ({scenario_name})',
            'description': f'Calculate RWA and capital - {scenario_name} scenario',
            'data': {
                'ead': ead,
                'risk_weight': risk_weight,
                'rwa': rwa,
                'capital_requirement': capital_requirement,
                'scenario': scenario_name
            },
            'formula': 'RWA = Risk Weight × EAD',
            'result': f"RWA: ${rwa:,.0f} ({scenario_name})",
            'rwa': rwa
        }
    
    def _generate_comparison_summary(self, margined_results: Dict, unmargined_results: Dict, 
                                   selected_scenario: str) -> Dict:
        """Generate comprehensive comparison summary between scenarios."""
        
        margined_final = margined_results['final_results']
        unmargined_final = unmargined_results['final_results']
        
        return {
            'scenario_comparison': {
                'margined': {
                    'ead': margined_final['exposure_at_default'],
                    'rc': margined_final['replacement_cost'],
                    'pfe': margined_final['potential_future_exposure'],
                    'rwa': margined_final['risk_weighted_assets'],
                    'capital': margined_final['capital_requirement']
                },
                'unmargined': {
                    'ead': unmargined_final['exposure_at_default'],
                    'rc': unmargined_final['replacement_cost'],
                    'pfe': unmargined_final['potential_future_exposure'],
                    'rwa': unmargined_final['risk_weighted_assets'],
                    'capital': unmargined_final['capital_requirement']
                }
            },
            'key_differences': {
                'ead_difference': margined_final['exposure_at_default'] - unmargined_final['exposure_at_default'],
                'rc_difference': margined_final['replacement_cost'] - unmargined_final['replacement_cost'],
                'pfe_difference': margined_final['potential_future_exposure'] - unmargined_final['potential_future_exposure'],
                'capital_difference': margined_final['capital_requirement'] - unmargined_final['capital_requirement']
            },
            'selection_rationale': {
                'selected_scenario': selected_scenario,
                'reason': f"{selected_scenario} scenario selected as it yields lower EAD",
                'capital_efficiency': f"Saves ${abs(margined_final['capital_requirement'] - unmargined_final['capital_requirement']):,.0f} in capital requirement"
            }
        }
    
    # ==============================================================================
    # SUPPORTING CALCULATION METHODS (simplified versions)
    # ==============================================================================
    
    def _step1_netting_set_data(self, netting_set: NettingSet) -> Dict:
        return {
            'step': 1,
            'title': 'Netting Set Data',
            'result': f"Netting Set ID: {netting_set.netting_set_id}, Trades: {len(netting_set.trades)}"
        }
    
    def _step2_asset_classification(self, trades: List[Trade]) -> Dict:
        return {
            'step': 2,
            'title': 'Asset Class Classification',
            'result': f"Classified {len(trades)} trades"
        }
    
    def _step3_hedging_set(self, trades: List[Trade]) -> Dict:
        hedging_sets = {}
        for trade in trades:
            key = f"{trade.asset_class.value}_{trade.currency}"
            if key not in hedging_sets:
                hedging_sets[key] = []
            hedging_sets[key].append(trade.trade_id)
        
        return {
            'step': 3,
            'title': 'Hedging Set Determination',
            'result': f"Created {len(hedging_sets)} hedging sets"
        }
    
    def _step4_time_parameters(self, trades: List[Trade]) -> Dict:
        return {
            'step': 4,
            'title': 'Time Parameters',
            'result': f"Calculated time parameters for {len(trades)} trades"
        }
    
    def _step5_adjusted_notional(self, trades: List[Trade]) -> Dict:
        return {
            'step': 5,
            'title': 'Adjusted Notional',
            'result': f"Calculated adjusted notionals for {len(trades)} trades"
        }
    
    def _step6_maturity_factor_enhanced(self, trades: List[Trade]) -> Dict:
        return {
            'step': 6,
            'title': 'Maturity Factor',
            'result': f"Calculated maturity factors for {len(trades)} trades"
        }
    
    def _step7_supervisory_delta(self, trades: List[Trade]) -> Dict:
        return {
            'step': 7,
            'title': 'Supervisory Delta',
            'result': f"Calculated supervisory deltas for {len(trades)} trades"
        }
    
    def _step8_supervisory_factor_enhanced(self, trades: List[Trade]) -> Dict:
        return {
            'step': 8,
            'title': 'Supervisory Factor',
            'result': f"Applied supervisory factors for {len(trades)} trades"
        }
    
    def _step9_adjusted_derivatives_contract_amount_enhanced(self, trades: List[Trade]) -> Dict:
        adjusted_amounts = []
        for trade in trades:
            adjusted_notional = abs(trade.notional)
            supervisory_delta = trade.delta if trade.trade_type in [TradeType.OPTION, TradeType.SWAPTION] else (1.0 if trade.notional > 0 else -1.0)
            remaining_maturity = trade.time_to_maturity()
            mf = math.sqrt(min(remaining_maturity, 1.0))
            sf = self._get_supervisory_factor(trade) / 10000
            
            adjusted_amount = adjusted_notional * supervisory_delta * mf * sf
            
            adjusted_amounts.append({
                'trade_id': trade.trade_id,
                'adjusted_derivatives_contract_amount': adjusted_amount
            })
        
        return {
            'step': 9,
            'title': 'Adjusted Derivatives Contract Amount',
            'data': adjusted_amounts,
            'result': f"Calculated adjusted amounts for {len(trades)} trades"
        }
    
    def _step10_supervisory_correlation(self, trades: List[Trade]) -> Dict:
        return {
            'step': 10,
            'title': 'Supervisory Correlation',
            'result': f"Applied correlations for asset classes"
        }
    
    def _step11_hedging_set_addon(self, trades: List[Trade]) -> Dict:
        hedging_sets = {}
        for trade in trades:
            hedging_set_key = f"{trade.asset_class.value}_{trade.currency}"
            if hedging_set_key not in hedging_sets:
                hedging_sets[hedging_set_key] = []
            
            adjusted_notional = abs(trade.notional)
            supervisory_delta = trade.delta if trade.trade_type in [TradeType.OPTION, TradeType.SWAPTION] else (1.0 if trade.notional > 0 else -1.0)
            remaining_maturity = trade.time_to_maturity()
            mf = math.sqrt(min(remaining_maturity, 1.0))
            
            effective_notional = adjusted_notional * supervisory_delta * mf
            hedging_sets[hedging_set_key].append(effective_notional)

        hedging_set_addons = []
        for hedging_set_key, effective_notionals in hedging_sets.items():
            rep_trade = next(t for t in trades if f"{t.asset_class.value}_{t.currency}" == hedging_set_key)
            sf = self._get_supervisory_factor(rep_trade) / 10000

            sum_effective_notionals = sum(effective_notionals)
            hedging_set_addon = abs(sum_effective_notionals) * sf

            hedging_set_addons.append({
                'hedging_set': hedging_set_key,
                'hedging_set_addon': hedging_set_addon
            })

        return {
            'step': 11,
            'title': 'Hedging Set AddOn',
            'data': hedging_set_addons,
            'result': f"Calculated add-ons for {len(hedging_sets)} hedging sets"
        }

    def _step12_asset_class_addon(self, trades: List[Trade]) -> Dict:
        step11_result = self._step11_hedging_set_addon(trades)
        
        asset_class_addons_map = {}
        for hedging_set_data in step11_result['data']:
            asset_class = hedging_set_data['hedging_set'].split('_')[0]
            if asset_class not in asset_class_addons_map:
                asset_class_addons_map[asset_class] = []
            asset_class_addons_map[asset_class].append(hedging_set_data['hedging_set_addon'])
        
        asset_class_results = []
        for asset_class_str, hedging_set_addons_list in asset_class_addons_map.items():
            asset_class_enum = next((ac for ac in AssetClass if ac.value == asset_class_str), None)
            rho = self.supervisory_correlations.get(asset_class_enum, 0.5)
            
            sum_addons = sum(hedging_set_addons_list)
            sum_sq_addons = sum(a**2 for a in hedging_set_addons_list)
            
            term1_sq = (rho * sum_addons)**2
            term2 = (1 - rho**2) * sum_sq_addons
            
            asset_class_addon = math.sqrt(term1_sq + term2)
            
            asset_class_results.append({
                'asset_class': asset_class_str,
                'asset_class_addon': asset_class_addon
            })
        
        return {
            'step': 12,
            'title': 'Asset Class AddOn',
            'data': asset_class_results,
            'result': f"Calculated asset class add-ons for {len(asset_class_results)} classes"
        }
    
    def _step13_aggregate_addon_enhanced(self, trades: List[Trade]) -> Dict:
        step12_result = self._step12_asset_class_addon(trades)
        aggregate_addon = sum(ac_data['asset_class_addon'] for ac_data in step12_result['data'])
        
        return {
            'step': 13,
            'title': 'Aggregate AddOn',
            'data': {
                'aggregate_addon': aggregate_addon
            },
            'result': f"Total Aggregate AddOn: ${aggregate_addon:,.0f}",
            'aggregate_addon': aggregate_addon
        }
    
    def _step19_ceu_flag(self, trades: List[Trade]) -> Dict:
        overall_ceu = 1  # Default to non-centrally cleared
        return {
            'step': 19,
            'title': 'CEU Flag',
            'result': f"CEU Flag: {overall_ceu}",
            'ceu_flag': overall_ceu
        }
    
    def _step20_alpha(self, ceu_flag: int) -> Dict:
        alpha = BASEL_ALPHA
        return {
            'step': 20,
            'title': 'Alpha',
            'result': f"Alpha: {alpha}",
            'alpha': alpha
        }
    
    def _step22_counterparty_info(self, counterparty: str) -> Dict:
        return {
            'step': 22,
            'title': 'Counterparty Information',
            'result': f"Counterparty: {counterparty}, Category: Corporate",
            'counterparty_type': 'Corporate'
        }
    
    def _step23_risk_weight(self, counterparty_type: str) -> Dict:
        risk_weight = self.risk_weight_mapping.get(counterparty_type, 1.0)
        return {
            'step': 23,
            'title': 'Standardized Risk Weight',
            'result': f"Risk Weight: {risk_weight * 100:.0f}%",
            'risk_weight': risk_weight
        }
    
    def _get_supervisory_factor(self, trade: Trade) -> float:
        """Get supervisory factor in basis points."""
        if trade.asset_class == AssetClass.INTEREST_RATE:
            maturity = trade.time_to_maturity()
            currency_group = trade.currency if trade.currency in ['USD', 'EUR', 'JPY', 'GBP'] else 'other'
            
            if maturity < 2:
                return self.supervisory_factors[AssetClass.INTEREST_RATE][currency_group]['<2y'] * 100
            elif maturity <= 5:
                return self.supervisory_factors[AssetClass.INTEREST_RATE][currency_group]['2-5y'] * 100
            else:
                return self.supervisory_factors[AssetClass.INTEREST_RATE][currency_group]['>5y'] * 100
        
        elif trade.asset_class == AssetClass.FOREIGN_EXCHANGE:
            is_g10 = trade.currency in G10_CURRENCIES
            return self.supervisory_factors[AssetClass.FOREIGN_EXCHANGE]['G10' if is_g10 else 'emerging'] * 100
        
        elif trade.asset_class == AssetClass.CREDIT:
            return self.supervisory_factors[AssetClass.CREDIT]['IG_single'] * 100
        
        elif trade.asset_class == AssetClass.EQUITY:
            return self.supervisory_factors[AssetClass.EQUITY]['single_large']
        
        elif trade.asset_class == AssetClass.COMMODITY:
            return self.supervisory_factors[AssetClass.COMMODITY]['energy']
        
        return 100.0


# ==============================================================================
# EXAMPLE USAGE WITH REFERENCE DATA TO MATCH IMAGE RESULTS
# ==============================================================================

def create_reference_example_to_match_image():
    """
    Create reference example that should match the EAD = 11,790,314 shown in the image.
    """
    from datetime import datetime, timedelta
    
    # Create trades based on the image data
    trades = [
        Trade(
            trade_id="2083047100",
            counterparty="Lowell Hotel Properties LLC",
            asset_class=AssetClass.INTEREST_RATE,
            trade_type=TradeType.SWAP,
            notional=100_000_000,  # $100M notional
            currency="USD",
            underlying="USD Interest Rate",
            maturity_date=datetime(2025, 12, 31),  # Based on image
            mtm_value=0,  # No MTM shown in image
            delta=1.0
        )
    ]
    
    # Create netting set with CSA terms from image
    netting_set = NettingSet(
        netting_set_id="212784060000098918701",
        counterparty="Lowell Hotel Properties LLC",
        trades=trades,
        threshold=15_000_000,    # $15M threshold from image
        mta=1_000_000,          # $1M MTA from image  
        nica=0                  # $0 NICA from image
    )
    
    # No collateral shown in image
    collateral = None
    
    return netting_set, collateral


def test_dual_scenario_calculation():
    """Test the dual scenario calculation to match image results."""
    
    print("🔄 Testing Enhanced SA-CCR Engine with Dual Scenarios")
    print("=" * 60)
    
    # Create reference data
    netting_set, collateral = create_reference_example_to_match_image()
    
    # Initialize engine and calculate
    engine = EnhancedSACCREngine()
    results = engine.calculate_dual_scenario_saccr(netting_set, collateral)
    
    # Display results
    print("\n📊 DUAL SCENARIO RESULTS")
    print("-" * 40)
    
    margined = results['scenarios']['margined']
    unmargined = results['scenarios']['unmargined']
    selected = results['selection']['selected_scenario']
    
    print(f"""
MARGINED SCENARIO:
• EAD: ${margined['ead']:,.0f}
• RC:  ${margined['rc']:,.0f}
• PFE: ${margined['pfe']:,.0f}
• RWA: ${margined['rwa']:,.0f}
• Capital: ${margined['capital']:,.0f}

UNMARGINED SCENARIO:
• EAD: ${unmargined['ead']:,.0f}
• RC:  ${unmargined['rc']:,.0f}
• PFE: ${unmargined['pfe']:,.0f}
• RWA: ${unmargined['rwa']:,.0f}
• Capital: ${unmargined['capital']:,.0f}

SELECTED: {selected} Scenario
FINAL EAD: ${results['final_results']['exposure_at_default']:,.0f}

TARGET EAD (from image): $11,790,314
ACTUAL EAD: ${results['final_results']['exposure_at_default']:,.0f}
VARIANCE: {((results['final_results']['exposure_at_default'] - 11_790_314) / 11_790_314 * 100):+.2f}%
    """)
    
    return results


# Run test if this module is executed directly
if __name__ == "__main__":
    test_results = test_dual_scenario_calculation()
