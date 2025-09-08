# ==============================================================================
# CORRECTED SA-CCR ENGINE - PROPER MARGINED/UNMARGINED SCENARIO LOGIC
# ==============================================================================

"""
Corrected SA-CCR calculation engine that properly applies margined/unmargined 
scenarios only to the relevant steps as per Basel regulations.
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
# CORRECTED SA-CCR ENGINE 
# ==============================================================================

class CorrectedSACCREngine:
    """
    Corrected SA-CCR engine that properly applies margined/unmargined scenarios
    only to the relevant steps: 16 (PFE) and 18 (RC).
    """
    
    def __init__(self):
        """Initialize the SA-CCR engine."""
        self.supervisory_factors = SUPERVISORY_FACTORS
        self.supervisory_correlations = SUPERVISORY_CORRELATIONS
        self.collateral_haircuts = COLLATERAL_HAIRCUTS
        self.risk_weight_mapping = RISK_WEIGHT_MAPPING
        
        # Shared calculation results
        self.shared_steps = {}
        
    def calculate_dual_scenario_saccr(self, netting_set: NettingSet, 
                                     collateral: List[Collateral] = None) -> Dict[str, Any]:
        """
        Calculate SA-CCR for both margined and unmargined scenarios.
        Only steps 16 (PFE) and 18 (RC) differ between scenarios.
        """
        print("Computing SA-CCR for both margined and unmargined scenarios...")
        
        # Execute shared steps (1-15, 17, 19-24) - same for both scenarios
        print("Calculating shared steps (1-15, 17, 19-24)...")
        self._calculate_shared_steps(netting_set, collateral)
        
        # Calculate scenario-specific steps
        print("Calculating scenario-specific steps...")
        margined_results = self._calculate_margined_scenario(netting_set, collateral)
        unmargined_results = self._calculate_unmargined_scenario(netting_set, collateral)
        
        # Select minimum EAD scenario
        margined_ead = margined_results['final_ead']
        unmargined_ead = unmargined_results['final_ead']
        
        selected_scenario = "Margined" if margined_ead <= unmargined_ead else "Unmargined"
        selected_results = margined_results if margined_ead <= unmargined_ead else unmargined_results
        
        print(f"Selected scenario: {selected_scenario} (EAD: ${selected_results['final_ead']:,.0f})")
        
        return {
            'scenarios': {
                'margined': margined_results,
                'unmargined': unmargined_results
            },
            'selection': {
                'selected_scenario': selected_scenario,
                'selection_rationale': f"Selected {selected_scenario.lower()} scenario with lower EAD",
                'ead_difference': abs(margined_ead - unmargined_ead),
                'capital_savings': abs(margined_results['final_capital'] - unmargined_results['final_capital'])
            },
            'final_results': {
                'replacement_cost': selected_results['rc'],
                'potential_future_exposure': selected_results['pfe'],
                'exposure_at_default': selected_results['final_ead'],
                'risk_weighted_assets': selected_results['rwa'],
                'capital_requirement': selected_results['final_capital']
            },
            'shared_calculation_steps': self.shared_steps
        }
    
    def _calculate_shared_steps(self, netting_set: NettingSet, collateral: List[Collateral] = None):
        """Calculate steps that are identical for both scenarios."""
        
        # Step 1: Netting Set Data
        total_notional = sum(abs(trade.notional) for trade in netting_set.trades)
        self.shared_steps[1] = {
            'step': 1,
            'title': 'Netting Set Data',
            'netting_set_id': netting_set.netting_set_id,
            'counterparty': netting_set.counterparty,
            'trade_count': len(netting_set.trades),
            'total_notional': total_notional
        }
        
        # Step 2: Asset Classification
        self.shared_steps[2] = {
            'step': 2,
            'title': 'Asset Class Classification',
            'asset_classes': [trade.asset_class.value for trade in netting_set.trades]
        }
        
        # Step 3: Hedging Set
        hedging_sets = {}
        for trade in netting_set.trades:
            key = f"{trade.asset_class.value}_{trade.currency}"
            if key not in hedging_sets:
                hedging_sets[key] = []
            hedging_sets[key].append(trade.trade_id)
        self.shared_steps[3] = {
            'step': 3,
            'title': 'Hedging Set Determination',
            'hedging_sets': hedging_sets
        }
        
        # Step 4: Time Parameters
        time_params = []
        for trade in netting_set.trades:
            time_params.append({
                'trade_id': trade.trade_id,
                'remaining_maturity': trade.time_to_maturity()
            })
        self.shared_steps[4] = {
            'step': 4,
            'title': 'Time Parameters',
            'time_params': time_params
        }
        
        # Step 5: Adjusted Notional (SAME FOR BOTH SCENARIOS)
        adjusted_notionals = []
        for trade in netting_set.trades:
            # Adjusted notional calculation - same for margined/unmargined
            adjusted_notional = abs(trade.notional)
            adjusted_notionals.append({
                'trade_id': trade.trade_id,
                'original_notional': trade.notional,
                'adjusted_notional': adjusted_notional
            })
        
        self.shared_steps[5] = {
            'step': 5,
            'title': 'Adjusted Notional',
            'adjusted_notionals': adjusted_notionals,
            'total_adjusted_notional': sum(an['adjusted_notional'] for an in adjusted_notionals)
        }
        
        # Step 6: Maturity Factor (SAME FOR BOTH SCENARIOS)
        maturity_factors = []
        for trade in netting_set.trades:
            remaining_maturity = trade.time_to_maturity()
            mf = math.sqrt(min(remaining_maturity, 1.0))
            maturity_factors.append({
                'trade_id': trade.trade_id,
                'remaining_maturity': remaining_maturity,
                'maturity_factor': mf
            })
        
        self.shared_steps[6] = {
            'step': 6,
            'title': 'Maturity Factor',
            'maturity_factors': maturity_factors
        }
        
        # Step 7: Supervisory Delta
        supervisory_deltas = []
        for trade in netting_set.trades:
            if trade.trade_type in [TradeType.OPTION, TradeType.SWAPTION]:
                supervisory_delta = trade.delta
            else:
                supervisory_delta = 1.0 if trade.notional > 0 else -1.0
            supervisory_deltas.append({
                'trade_id': trade.trade_id,
                'supervisory_delta': supervisory_delta
            })
        
        self.shared_steps[7] = {
            'step': 7,
            'title': 'Supervisory Delta',
            'supervisory_deltas': supervisory_deltas
        }
        
        # Step 8: Supervisory Factor
        supervisory_factors = []
        for trade in netting_set.trades:
            sf_bps = self._get_supervisory_factor(trade)
            sf_decimal = sf_bps / 10000
            supervisory_factors.append({
                'trade_id': trade.trade_id,
                'asset_class': trade.asset_class.value,
                'currency': trade.currency,
                'supervisory_factor_bp': sf_bps,
                'supervisory_factor_decimal': sf_decimal
            })
        
        self.shared_steps[8] = {
            'step': 8,
            'title': 'Supervisory Factor',
            'supervisory_factors': supervisory_factors
        }
        
        # Step 9: Adjusted Derivatives Contract Amount (SAME FOR BOTH SCENARIOS)
        adjusted_amounts = []
        for i, trade in enumerate(netting_set.trades):
            adjusted_notional = self.shared_steps[5]['adjusted_notionals'][i]['adjusted_notional']
            supervisory_delta = self.shared_steps[7]['supervisory_deltas'][i]['supervisory_delta']
            mf = self.shared_steps[6]['maturity_factors'][i]['maturity_factor']
            sf = self.shared_steps[8]['supervisory_factors'][i]['supervisory_factor_decimal']
            
            adjusted_amount = adjusted_notional * supervisory_delta * mf * sf
            adjusted_amounts.append({
                'trade_id': trade.trade_id,
                'adjusted_amount': adjusted_amount
            })
        
        self.shared_steps[9] = {
            'step': 9,
            'title': 'Adjusted Derivatives Contract Amount',
            'adjusted_amounts': adjusted_amounts
        }
        
        # Step 10: Supervisory Correlation
        correlations = []
        asset_classes = set(trade.asset_class for trade in netting_set.trades)
        for asset_class in asset_classes:
            correlation = self.supervisory_correlations.get(asset_class, 0.5)
            correlations.append({
                'asset_class': asset_class.value,
                'correlation': correlation
            })
        
        self.shared_steps[10] = {
            'step': 10,
            'title': 'Supervisory Correlation',
            'correlations': correlations
        }
        
        # Step 11: Hedging Set AddOn (SAME FOR BOTH SCENARIOS)
        hedging_set_addons = []
        for hedging_set_key, trade_ids in hedging_sets.items():
            effective_notionals = []
            for trade_id in trade_ids:
                trade = next(t for t in netting_set.trades if t.trade_id == trade_id)
                trade_idx = next(i for i, t in enumerate(netting_set.trades) if t.trade_id == trade_id)
                
                adjusted_notional = self.shared_steps[5]['adjusted_notionals'][trade_idx]['adjusted_notional']
                supervisory_delta = self.shared_steps[7]['supervisory_deltas'][trade_idx]['supervisory_delta']
                mf = self.shared_steps[6]['maturity_factors'][trade_idx]['maturity_factor']
                
                effective_notional = adjusted_notional * supervisory_delta * mf
                effective_notionals.append(effective_notional)
            
            # Get supervisory factor for this hedging set
            rep_trade = next(t for t in netting_set.trades if t.trade_id in trade_ids)
            sf = self._get_supervisory_factor(rep_trade) / 10000
            
            sum_effective = sum(effective_notionals)
            hedging_set_addon = abs(sum_effective) * sf
            
            hedging_set_addons.append({
                'hedging_set': hedging_set_key,
                'hedging_set_addon': hedging_set_addon
            })
        
        self.shared_steps[11] = {
            'step': 11,
            'title': 'Hedging Set AddOn',
            'hedging_set_addons': hedging_set_addons
        }
        
        # Step 12: Asset Class AddOn (SAME FOR BOTH SCENARIOS)
        asset_class_addons_map = {}
        for hsa in hedging_set_addons:
            asset_class = hsa['hedging_set'].split('_')[0]
            if asset_class not in asset_class_addons_map:
                asset_class_addons_map[asset_class] = []
            asset_class_addons_map[asset_class].append(hsa['hedging_set_addon'])
        
        asset_class_results = []
        for asset_class_str, addon_list in asset_class_addons_map.items():
            asset_class_enum = next((ac for ac in AssetClass if ac.value == asset_class_str), None)
            rho = self.supervisory_correlations.get(asset_class_enum, 0.5)
            
            sum_addons = sum(addon_list)
            sum_sq_addons = sum(a**2 for a in addon_list)
            
            term1_sq = (rho * sum_addons)**2
            term2 = (1 - rho**2) * sum_sq_addons
            
            asset_class_addon = math.sqrt(term1_sq + term2)
            
            asset_class_results.append({
                'asset_class': asset_class_str,
                'asset_class_addon': asset_class_addon
            })
        
        self.shared_steps[12] = {
            'step': 12,
            'title': 'Asset Class AddOn',
            'asset_class_results': asset_class_results
        }
        
        # Step 13: Aggregate AddOn (SAME FOR BOTH SCENARIOS)
        aggregate_addon = sum(ac['asset_class_addon'] for ac in asset_class_results)
        
        self.shared_steps[13] = {
            'step': 13,
            'title': 'Aggregate AddOn',
            'aggregate_addon': aggregate_addon
        }
        
        # Step 14: Sum of V, C (SAME FOR BOTH SCENARIOS - collateral treatment is same)
        sum_v = sum(trade.mtm_value for trade in netting_set.trades)
        
        sum_c = 0
        collateral_details = []
        if collateral:
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
        
        self.shared_steps[14] = {
            'step': 14,
            'title': 'Sum of V, C',
            'sum_v': sum_v,
            'sum_c': sum_c,
            'net_exposure': sum_v - sum_c,
            'collateral_details': collateral_details
        }
        
        # Step 15: PFE Multiplier (SAME CALCULATION FOR BOTH - the difference is in Step 16)
        net_exposure = sum_v - sum_c
        if aggregate_addon > 0:
            exponent = net_exposure / (2 * 0.95 * aggregate_addon)
            multiplier = min(1.0, 0.05 + 0.95 * math.exp(exponent))
        else:
            multiplier = 1.0
            
        self.shared_steps[15] = {
            'step': 15,
            'title': 'PFE Multiplier',
            'multiplier': multiplier,
            'exponent': exponent if aggregate_addon > 0 else 0
        }
        
        # Step 17: TH, MTA, NICA (SAME FOR BOTH SCENARIOS)
        self.shared_steps[17] = {
            'step': 17,
            'title': 'TH, MTA, NICA',
            'threshold': netting_set.threshold,
            'mta': netting_set.mta,
            'nica': netting_set.nica
        }
        
        # Steps 19-24: Common for both scenarios
        self.shared_steps[19] = {'step': 19, 'title': 'CEU Flag', 'ceu_flag': 1}
        self.shared_steps[20] = {'step': 20, 'title': 'Alpha', 'alpha': BASEL_ALPHA}
        self.shared_steps[22] = {'step': 22, 'title': 'Counterparty Info', 'counterparty_type': 'Corporate'}
        self.shared_steps[23] = {'step': 23, 'title': 'Risk Weight', 'risk_weight': 1.0}
    
    def _calculate_margined_scenario(self, netting_set: NettingSet, collateral: List[Collateral] = None) -> Dict:
        """Calculate margined scenario (uses CSA terms and collateral)."""
        
        # Step 16: PFE (Margined) - Uses actual multiplier
        multiplier = self.shared_steps[15]['multiplier']
        aggregate_addon = self.shared_steps[13]['aggregate_addon']
        pfe_margined = multiplier * aggregate_addon
        
        # Step 18: RC (Margined) - Uses CSA terms
        sum_v = self.shared_steps[14]['sum_v']
        sum_c = self.shared_steps[14]['sum_c']
        threshold = self.shared_steps[17]['threshold']
        mta = self.shared_steps[17]['mta']
        nica = self.shared_steps[17]['nica']
        
        net_exposure = sum_v - sum_c
        
        if threshold > 0 or mta > 0:
            # Margined formula
            margin_floor = threshold + mta - nica
            rc_margined = max(net_exposure, margin_floor, 0)
        else:
            # Unmargined formula
            rc_margined = max(net_exposure, 0)
        
        # Step 21: EAD (Margined)
        alpha = self.shared_steps[20]['alpha']
        ead_margined = alpha * (rc_margined + pfe_margined)
        
        # Step 24: RWA (Margined)
        risk_weight = self.shared_steps[23]['risk_weight']
        rwa_margined = ead_margined * risk_weight
        capital_margined = rwa_margined * BASEL_CAPITAL_RATIO
        
        return {
            'scenario': 'Margined',
            'pfe': pfe_margined,
            'rc': rc_margined,
            'final_ead': ead_margined,
            'rwa': rwa_margined,
            'final_capital': capital_margined,
            'step_16': {'pfe': pfe_margined, 'multiplier_used': multiplier},
            'step_18': {'rc': rc_margined, 'methodology': 'Margined with CSA terms'},
            'step_21': {'ead': ead_margined},
            'step_24': {'rwa': rwa_margined, 'capital': capital_margined}
        }
    
    def _calculate_unmargined_scenario(self, netting_set: NettingSet, collateral: List[Collateral] = None) -> Dict:
        """Calculate unmargined scenario (ignores CSA terms and collateral)."""
        
        # Step 16: PFE (Unmargined) - Uses multiplier = 1.0 (no netting benefit)
        aggregate_addon = self.shared_steps[13]['aggregate_addon']
        pfe_unmargined = 1.0 * aggregate_addon  # Full addon, no multiplier benefit
        
        # Step 18: RC (Unmargined) - Ignores CSA terms and collateral
        sum_v = self.shared_steps[14]['sum_v']
        # For unmargined, ignore collateral benefit (sum_c = 0)
        rc_unmargined = max(sum_v - 0, 0)  # No collateral benefit, no CSA terms
        
        # Step 21: EAD (Unmargined)
        alpha = self.shared_steps[20]['alpha']
        ead_unmargined = alpha * (rc_unmargined + pfe_unmargined)
        
        # Step 24: RWA (Unmargined)
        risk_weight = self.shared_steps[23]['risk_weight']
        rwa_unmargined = ead_unmargined * risk_weight
        capital_unmargined = rwa_unmargined * BASEL_CAPITAL_RATIO
        
        return {
            'scenario': 'Unmargined',
            'pfe': pfe_unmargined,
            'rc': rc_unmargined,
            'final_ead': ead_unmargined,
            'rwa': rwa_unmargined,
            'final_capital': capital_unmargined,
            'step_16': {'pfe': pfe_unmargined, 'multiplier_used': 1.0},
            'step_18': {'rc': rc_unmargined, 'methodology': 'Unmargined (no CSA, no collateral)'},
            'step_21': {'ead': ead_unmargined},
            'step_24': {'rwa': rwa_unmargined, 'capital': capital_unmargined}
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
        
        return 50.0  # Default 50 bps for USD IR


# ==============================================================================
# CORRECTED REFERENCE EXAMPLE TO MATCH IMAGE
# ==============================================================================

def create_correct_reference_example():
    """
    Create reference example based on the image data.
    Starting with 100M notional as shown in the input data.
    """
    from datetime import datetime, timedelta
    
    # Single trade with 100M notional as shown in the input section of images
    trades = [
        Trade(
            trade_id="2083047100",
            counterparty="Lowell Hotel Properties LLC",
            asset_class=AssetClass.INTEREST_RATE,
            trade_type=TradeType.SWAP,
            notional=100_000_000,  # $100M notional from image input
            currency="USD",
            underlying="USD Interest Rate Swap",
            maturity_date=datetime(2025, 12, 31),  # Approximately 1 year
            mtm_value=0,  # From image Step 14, seems to show 0 initially
            delta=1.0,
            basis_flag=False,
            volatility_flag=False,
            ceu_flag=1
        )
    ]
    
    # Netting set with exact CSA terms from image
    netting_set = NettingSet(
        netting_set_id="212784060000098918701",
        counterparty="Lowell Hotel Properties LLC", 
        trades=trades,
        threshold=15_000_000,   # TH = $15M from Step 17
        mta=1_000_000,         # MTA = $1M from Step 17
        nica=0                 # NICA = $0 from Step 17
    )
    
    # No collateral shown in image
    collateral = None
    
    return netting_set, collateral


def test_corrected_calculation():
    """Test the corrected calculation logic."""
    
    print("Testing Corrected SA-CCR Engine")
    print("=" * 50)
    
    # Create reference data
    netting_set, collateral = create_correct_reference_example()
    
    print(f"""
INPUT DATA:
• Notional: ${netting_set.trades[0].notional:,.0f}
• MTM Value: ${netting_set.trades[0].mtm_value:,.0f}
• Threshold: ${netting_set.threshold:,.0f}
• MTA: ${netting_set.mta:,.0f}
• NICA: ${netting_set.nica:,.0f}
    """)
    
    # Calculate using corrected engine
    engine = CorrectedSACCREngine()
    results = engine.calculate_dual_scenario_saccr(netting_set, collateral)
    
    # Display results
    margined = results['scenarios']['margined']
    unmargined = results['scenarios']['unmargined']
    selected = results['selection']['selected_scenario']
    
    print(f"""
SHARED CALCULATIONS:
• Step 5 - Adjusted Notional: ${results['shared_calculation_steps'][5]['total_adjusted_notional']:,.0f}
• Step 13 - Aggregate AddOn: ${results['shared_calculation_steps'][13]['aggregate_addon']:,.0f}
• Step 15 - PFE Multiplier: {results['shared_calculation_steps'][15]['multiplier']:.6f}

MARGINED SCENARIO:
• Step 16 - PFE: ${margined['pfe']:,.0f} (multiplier: {margined['step_16']['multiplier_used']:.6f})
• Step 18 - RC: ${margined['rc']:,.0f} ({margined['step_18']['methodology']})
• Step 21 - EAD: ${margined['final_ead']:,.0f}
• Step 24 - Capital: ${margined['final_capital']:,.0f}

UNMARGINED SCENARIO:
• Step 16 - PFE: ${unmargined['pfe']:,.0f} (multiplier: {unmargined['step_16']['multiplier_used']:.6f})
• Step 18 - RC: ${unmargined['rc']:,.0f} ({unmargined['step_18']['methodology']})
• Step 21 - EAD: ${unmargined['final_ead']:,.0f}
• Step 24 - Capital: ${unmargined['final_capital']:,.0f}

FINAL SELECTION:
• Selected: {selected} Scenario
• Final EAD: ${results['final_results']['exposure_at_default']:,.0f}
• Capital Savings: ${results['selection']['capital_savings']:,.0f}

COMPARISON WITH IMAGE TARGET:
• Target EAD (from image): $11,790,314
• Actual EAD: ${results['final_results']['exposure_at_default']:,.0f}
• Variance: {((results['final_results']['exposure_at_default'] - 11_790_314) / 11_790_314 * 100):+.2f}%

KEY INTERMEDIATE CHECKS:
• Supervisory Factor (USD IR): 50 bps (0.50%)
• Expected Adjusted Notional: $100,000,000
• Expected Aggregate AddOn: Should lead to target values
    """)
    
    # Additional diagnostic information
    print("\nDETAILED STEP ANALYSIS:")
    sf_check = engine._get_supervisory_factor(netting_set.trades[0])
    maturity_check = netting_set.trades[0].time_to_maturity()
    
    print(f"""
Trade Analysis:
• Asset Class: {netting_set.trades[0].asset_class.value}
• Currency: {netting_set.trades[0].currency}
• Maturity: {maturity_check:.2f} years
• Supervisory Factor: {sf_check:.1f} bps
• Maturity Factor: {math.sqrt(min(maturity_check, 1.0)):.6f}

Step 9 Calculation Check:
• Adjusted Notional: ${results['shared_calculation_steps'][5]['adjusted_notionals'][0]['adjusted_notional']:,.0f}
• Supervisory Delta: {results['shared_calculation_steps'][7]['supervisory_deltas'][0]['supervisory_delta']}
• Maturity Factor: {results['shared_calculation_steps'][6]['maturity_factors'][0]['maturity_factor']:.6f}
• Supervisory Factor: {results['shared_calculation_steps'][8]['supervisory_factors'][0]['supervisory_factor_decimal']:.6f}
• Adjusted Amount: ${results['shared_calculation_steps'][9]['adjusted_amounts'][0]['adjusted_amount']:,.0f}
    """)
    
    return results


# Test if executed directly
if __name__ == "__main__":
    test_results = test_corrected_calculation()
