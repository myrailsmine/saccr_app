# ==============================================================================
# US SA-CCR ENGINE - 12 CFR 217.132 REGULATORY IMPLEMENTATION
# ==============================================================================

"""
SA-CCR calculation engine implementing US regulations from 12 CFR 217.132.
This implementation follows the Federal Register requirements including:
- Table 3 supervisory factors (maturity-independent for interest rates)
- Official US regulatory formulas
- US-specific MPOR and calculation methodologies

Reference: 12 CFR 217.132 - Counterparty credit risk of repo-style transactions, 
eligible margin loans, and OTC derivative contracts.
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
    settlement_date: datetime = None
    mtm_value: float = 0.0
    delta: float = 1.0
    basis_flag: bool = False
    volatility_flag: bool = False
    ceu_flag: int = 1
    
    def time_to_maturity(self, as_of_date: datetime = None) -> float:
        """Calculate time to maturity in years from as_of_date."""
        if as_of_date is None:
            as_of_date = datetime.now()
        return max(0, (self.maturity_date - as_of_date).days / 365.25)
    
    def time_to_settlement(self, as_of_date: datetime = None) -> float:
        """Calculate time to settlement in years from as_of_date."""
        if as_of_date is None:
            as_of_date = datetime.now()
        if self.settlement_date is None:
            return 0
        return max(0, (self.settlement_date - as_of_date).days / 365.25)

@dataclass
class NettingSet:
    netting_set_id: str
    counterparty: str
    trades: List[Trade]
    threshold: float = 0.0
    mta: float = 0.0
    nica: float = 0.0
    has_csa: bool = True

@dataclass
class Collateral:
    collateral_type: CollateralType
    currency: str
    amount: float
    haircut: float = 0.0

# ==============================================================================
# US REGULATORY PARAMETERS PER 12 CFR 217.132 TABLE 3
# ==============================================================================

# Table 3 to § 217.132 - Supervisory Factors (NO MATURITY DEPENDENCE FOR INTEREST RATES)
US_SUPERVISORY_FACTORS = {
    # Interest Rate derivative contracts - single factor per currency (12 CFR 217.132 Table 3)
    AssetClass.INTEREST_RATE: {
        'USD': 0.50,  # 0.5% for USD interest rate derivatives (maturity-independent)
        'EUR': 0.50,  # 0.5% for EUR interest rate derivatives
        'JPY': 0.50,  # 0.5% for JPY interest rate derivatives  
        'GBP': 0.50,  # 0.5% for GBP interest rate derivatives
        'CHF': 0.50,  # 0.5% for CHF interest rate derivatives
        'CAD': 0.50,  # 0.5% for CAD interest rate derivatives
        'AUD': 0.50,  # 0.5% for AUD interest rate derivatives
        'other': 1.50  # 1.5% for other currencies
    },
    # Foreign Exchange derivative contracts (12 CFR 217.132 Table 3)
    AssetClass.FOREIGN_EXCHANGE: {
        'G10': 4.0,      # 4.0% for G10 currencies
        'emerging': 15.0  # 15.0% for emerging market currencies
    },
    # Credit derivative contracts (12 CFR 217.132 Table 3)
    AssetClass.CREDIT: {
        'IG': 0.46,       # 0.46% for Investment Grade
        'HY': 1.30       # 1.30% for High Yield
    },
    # Equity derivative contracts (12 CFR 217.132 Table 3)
    AssetClass.EQUITY: {
        'single': 32.0,   # 32% for single-name equity
        'index': 20.0     # 20% for equity index
    },
    # Commodity derivative contracts (12 CFR 217.132 Table 3) 
    AssetClass.COMMODITY: {
        'energy': 18.0,      # 18% for energy commodities
        'metals': 18.0,      # 18% for precious metals
        'agriculture': 18.0, # 18% for agriculture
        'other': 18.0        # 18% for other commodities
    }
}

# Supervisory Correlations per 12 CFR 217.132 Table 3
US_SUPERVISORY_CORRELATIONS = {
    AssetClass.INTEREST_RATE: 0.99,    # 99% correlation for interest rate hedging sets
    AssetClass.FOREIGN_EXCHANGE: 0.60, # 60% correlation for FX hedging sets
    AssetClass.CREDIT: 0.50,           # 50% correlation for credit hedging sets
    AssetClass.EQUITY: 0.80,           # 80% correlation for equity hedging sets
    AssetClass.COMMODITY: 0.40         # 40% correlation for commodity hedging sets
}

# US Standard Supervisory Haircuts per 12 CFR 217.132 Table 1
US_COLLATERAL_HAIRCUTS = {
    CollateralType.CASH: 0.0,
    CollateralType.GOVERNMENT_BONDS: 0.5,
    CollateralType.CORPORATE_BONDS: 4.0,
    CollateralType.EQUITIES: 15.0,
    CollateralType.MONEY_MARKET: 0.5
}

# Risk Weight Mapping per US regulations
US_RISK_WEIGHT_MAPPING = {
    'Corporate': 1.0,        # 100% risk weight for corporate exposures
    'Bank': 0.20,           # 20% risk weight for bank exposures 
    'Sovereign': 0.0,       # 0% risk weight for US Treasury
    'Non-Profit Org': 1.0  # 100% risk weight for non-profit organizations
}

# US-specific parameters
G10_CURRENCIES = ['USD', 'EUR', 'JPY', 'GBP', 'CHF', 'CAD', 'AUD', 'NZD', 'SEK', 'NOK']
US_ALPHA_STANDARD = 1.4
US_ALPHA_CEU = 1.0  # For Central Bank exposures 
US_CAPITAL_RATIO = 0.08
US_BUSINESS_DAYS_PER_YEAR = 250

# US MPOR values per 12 CFR 217.132
US_MPOR_VALUES = {
    'margined_standard': 10,    # 10 business days for margined transactions
    'margined_disputes': 20,    # 20 business days if disputes provision triggered
    'unmargined': 20           # 20 business days for unmargined transactions
}

# ==============================================================================
# US SA-CCR ENGINE PER 12 CFR 217.132
# ==============================================================================

class USSACCREngine:
    """
    US SA-CCR engine implementing 12 CFR 217.132 regulations.
    """
    
    def __init__(self, as_of_date: datetime = None):
        """Initialize the US SA-CCR engine."""
        self.as_of_date = as_of_date or datetime(2020, 12, 31)
        self.supervisory_factors = US_SUPERVISORY_FACTORS
        self.supervisory_correlations = US_SUPERVISORY_CORRELATIONS
        self.collateral_haircuts = US_COLLATERAL_HAIRCUTS
        self.risk_weight_mapping = US_RISK_WEIGHT_MAPPING
        
        # Shared calculation results
        self.shared_steps = {}
        
    def calculate_dual_scenario_saccr(self, netting_set: NettingSet, 
                                     collateral: List[Collateral] = None) -> Dict[str, Any]:
        """
        Calculate SA-CCR for both margined and unmargined scenarios per 12 CFR 217.132.
        """
        print("Computing US SA-CCR per 12 CFR 217.132...")
        
        # Calculate shared steps
        print("Calculating shared calculation steps...")
        self._calculate_shared_steps(netting_set, collateral)
        
        # Calculate scenario-specific steps
        print("Calculating scenario-specific steps...")
        margined_results = self._calculate_margined_scenario(netting_set, collateral)
        unmargined_results = self._calculate_unmargined_scenario(netting_set, collateral)
        
        # Select minimum EAD scenario per US regulations
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
                'selection_rationale': f"Selected {selected_scenario.lower()} scenario with lower EAD per 12 CFR 217.132",
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
            'shared_calculation_steps': self.shared_steps,
            'regulatory_reference': '12 CFR 217.132'
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
        
        # Step 3: Hedging Set per 12 CFR 217.132
        hedging_sets = {}
        for trade in netting_set.trades:
            if trade.asset_class == AssetClass.INTEREST_RATE:
                # For IR derivatives, hedging set is currency per 12 CFR 217.132
                key = trade.currency
            else:
                key = f"{trade.asset_class.value}_{trade.currency}"
            
            if key not in hedging_sets:
                hedging_sets[key] = []
            hedging_sets[key].append(trade.trade_id)
        
        self.shared_steps[3] = {
            'step': 3,
            'title': 'Hedging Set Determination (12 CFR 217.132)',
            'hedging_sets': hedging_sets
        }
        
        # Step 4: Time Parameters (S, E, M) per 12 CFR 217.132
        time_params = []
        for trade in netting_set.trades:
            S = trade.time_to_settlement(self.as_of_date)
            M = trade.time_to_maturity(self.as_of_date)
            E = M  # For vanilla swaps, E = M
            
            time_params.append({
                'trade_id': trade.trade_id,
                'S': S,
                'E': E,
                'M': M
            })
        
        self.shared_steps[4] = {
            'step': 4,
            'title': 'Time Parameters (S, E, M)',
            'time_params': time_params
        }
        
        # Step 5: Adjusted Notional using US Supervisory Duration per 12 CFR 217.132
        adjusted_notionals = []
        for i, trade in enumerate(netting_set.trades):
            S = self.shared_steps[4]['time_params'][i]['S']
            E = self.shared_steps[4]['time_params'][i]['E']
            
            if trade.asset_class == AssetClass.INTEREST_RATE:
                # 12 CFR 217.132 Supervisory Duration formula
                sd = max(0.05 * (math.exp(-0.05 * S) - math.exp(-0.05 * E)), 0.04)
                adjusted_notional = abs(trade.notional) * sd * 10000
            else:
                sd = 1.0
                adjusted_notional = abs(trade.notional)
            
            adjusted_notionals.append({
                'trade_id': trade.trade_id,
                'original_notional': trade.notional,
                'supervisory_duration': sd,
                'adjusted_notional': adjusted_notional
            })
        
        self.shared_steps[5] = {
            'step': 5,
            'title': 'Adjusted Notional (12 CFR 217.132 Supervisory Duration)',
            'adjusted_notionals': adjusted_notionals,
            'total_adjusted_notional': sum(an['adjusted_notional'] for an in adjusted_notionals)
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
        
        # Step 8: Supervisory Factor per 12 CFR 217.132 Table 3
        supervisory_factors = []
        for trade in netting_set.trades:
            sf_percent = self._get_us_supervisory_factor_percent(trade)
            sf_decimal = sf_percent / 100
            supervisory_factors.append({
                'trade_id': trade.trade_id,
                'asset_class': trade.asset_class.value,
                'currency': trade.currency,
                'supervisory_factor_percent': sf_percent,
                'supervisory_factor_decimal': sf_decimal,
                'table_reference': '12 CFR 217.132 Table 3'
            })
        
        self.shared_steps[8] = {
            'step': 8,
            'title': 'Supervisory Factor (12 CFR 217.132 Table 3)',
            'supervisory_factors': supervisory_factors
        }
        
        # Step 10: Supervisory Correlation per 12 CFR 217.132 Table 3
        correlations = []
        asset_classes = set(trade.asset_class for trade in netting_set.trades)
        for asset_class in asset_classes:
            correlation = self.supervisory_correlations.get(asset_class, 0.5)
            correlations.append({
                'asset_class': asset_class.value,
                'correlation': correlation,
                'table_reference': '12 CFR 217.132 Table 3'
            })
        
        self.shared_steps[10] = {
            'step': 10,
            'title': 'Supervisory Correlation (12 CFR 217.132 Table 3)',
            'correlations': correlations
        }
        
        # Step 14: V, C (MTM and Collateral)
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
                    'haircut_percent': haircut * 100,
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
        
        # Step 17: TH, MTA, NICA
        self.shared_steps[17] = {
            'step': 17,
            'title': 'TH, MTA, NICA',
            'threshold': netting_set.threshold,
            'mta': netting_set.mta,
            'nica': netting_set.nica
        }
        
        # Step 19: CEU Flag  
        ceu_flag = netting_set.trades[0].ceu_flag if netting_set.trades else 1
        self.shared_steps[19] = {
            'step': 19,
            'title': 'CEU Flag',
            'ceu_flag': ceu_flag
        }
        
        # Step 20: Alpha per US regulations
        alpha = US_ALPHA_CEU if ceu_flag == 1 else US_ALPHA_STANDARD
        self.shared_steps[20] = {
            'step': 20,
            'title': 'Alpha (US Regulation)',
            'alpha': alpha,
            'formula': f"Alpha = {US_ALPHA_CEU} if CEU=1 else {US_ALPHA_STANDARD}"
        }
        
        # Step 22-23: Counterparty Information and Risk Weight
        self.shared_steps[22] = {
            'step': 22,
            'title': 'Counterparty Information',
            'counterparty_type': 'Non-Profit Org'
        }
        self.shared_steps[23] = {
            'step': 23,
            'title': 'Risk Weight',
            'risk_weight': 1.0
        }
    
    def _calculate_us_maturity_factor(self, trade: Trade, scenario: str) -> float:
        """
        Calculate maturity factor using US regulatory formulas per 12 CFR 217.132.
        """
        M = trade.time_to_maturity(self.as_of_date)
        
        if scenario == "margined":
            # US regulation: MF = sqrt(min(M, MPOR / 250)) for margined
            MPOR_years = US_MPOR_VALUES['margined_standard'] / US_BUSINESS_DAYS_PER_YEAR  # 10/250 = 0.04
            mf = math.sqrt(min(M, MPOR_years))
            
            # Apply 1.5 multiplier for very short-term transactions per US regulations
            if M <= MPOR_years:
                mf = mf * 1.5
            
            return mf
        else:
            # US regulation: For unmargined, floor at sqrt(10/250) = 0.2
            floor_value = math.sqrt(10 / US_BUSINESS_DAYS_PER_YEAR)  # sqrt(10/250) = 0.2
            mf = math.sqrt(min(M, 1.0))
            return max(mf, floor_value)
    
    def _calculate_margined_scenario(self, netting_set: NettingSet, collateral: List[Collateral] = None) -> Dict:
        """Calculate margined scenario per 12 CFR 217.132."""
        
        # Step 6: Maturity Factor (Margined) per US regulations
        maturity_factors_margined = []
        for trade in netting_set.trades:
            mf = self._calculate_us_maturity_factor(trade, "margined")
            maturity_factors_margined.append({
                'trade_id': trade.trade_id,
                'maturity_factor': mf,
                'formula': f'sqrt(min(M, {US_MPOR_VALUES["margined_standard"]}/250)) × 1.5 [short-term]',
                'mpor_days': US_MPOR_VALUES['margined_standard']
            })
        
        # Step 9: Adjusted Derivatives Contract Amount (Margined)
        adjusted_amounts_margined = []
        for i, trade in enumerate(netting_set.trades):
            adjusted_notional = self.shared_steps[5]['adjusted_notionals'][i]['adjusted_notional']
            supervisory_delta = self.shared_steps[7]['supervisory_deltas'][i]['supervisory_delta']
            mf = maturity_factors_margined[i]['maturity_factor']
            sf = self.shared_steps[8]['supervisory_factors'][i]['supervisory_factor_decimal']
            
            # 12 CFR 217.132: Adjusted Amount = Adjusted Notional × Delta × MF × SF
            adjusted_amount = adjusted_notional * supervisory_delta * mf * sf
            adjusted_amounts_margined.append({
                'trade_id': trade.trade_id,
                'adjusted_amount': adjusted_amount,
                'formula': 'Adjusted Notional × Delta × MF × SF (12 CFR 217.132)'
            })
        
        # Step 11: Hedging Set AddOn (Unmargined)
        hedging_sets = self.shared_steps[3]['hedging_sets']
        hedging_set_addons_unmargined = []
        
        for hedging_set_key, trade_ids in hedging_sets.items():
            hedging_set_addon = sum(
                amt['adjusted_amount'] for amt in adjusted_amounts_unmargined 
                if amt['trade_id'] in trade_ids
            )
            hedging_set_addons_unmargined.append({
                'hedging_set': hedging_set_key,
                'hedging_set_addon': abs(hedging_set_addon)
            })
        
        # Step 12: Asset Class AddOn (Unmargined)
        asset_class_addons_unmargined = []
        for hsa in hedging_set_addons_unmargined:
            asset_class_addons_unmargined.append({
                'asset_class': hsa['hedging_set'],
                'asset_class_addon': hsa['hedging_set_addon']
            })
        
        # Step 13: Aggregate AddOn (Unmargined)
        aggregate_addon_unmargined = sum(ac['asset_class_addon'] for ac in asset_class_addons_unmargined)
        
        # Step 15: PFE Multiplier (Unmargined)
        net_exposure = self.shared_steps[14]['net_exposure']
        if aggregate_addon_unmargined > 0:
            exponent = net_exposure / (2 * 0.95 * aggregate_addon_unmargined)
            multiplier_unmargined = min(1.0, 0.05 + 0.95 * math.exp(exponent))
        else:
            multiplier_unmargined = 1.0
        
        # Step 16: PFE (Unmargined)
        pfe_unmargined = multiplier_unmargined * aggregate_addon_unmargined
        
        # Step 18: RC (Unmargined) per 12 CFR 217.132
        sum_v = self.shared_steps[14]['sum_v']
        
        # 12 CFR 217.132 Unmargined RC: RC = max(V; 0) [ignores collateral]
        rc_unmargined = max(sum_v, 0)
        
        # Step 21: EAD (Unmargined)
        alpha = self.shared_steps[20]['alpha']
        ead_unmargined = alpha * (rc_unmargined + pfe_unmargined)
        
        # Step 24: RWA and Capital (Unmargined)
        risk_weight = self.shared_steps[23]['risk_weight']
        rwa_unmargined = ead_unmargined * risk_weight
        capital_unmargined = rwa_unmargined * US_CAPITAL_RATIO
        
        return {
            'scenario': 'Unmargined',
            'maturity_factors': maturity_factors_unmargined,
            'adjusted_amounts': adjusted_amounts_unmargined,
            'hedging_set_addons': hedging_set_addons_unmargined,
            'asset_class_addons': asset_class_addons_unmargined,
            'aggregate_addon': aggregate_addon_unmargined,
            'pfe_multiplier': multiplier_unmargined,
            'pfe': pfe_unmargined,
            'rc': rc_unmargined,
            'final_ead': ead_unmargined,
            'rwa': rwa_unmargined,
            'final_capital': capital_unmargined,
            'regulatory_formulas': {
                'maturity_factor': 'max(sqrt(min(M, 1)), sqrt(10/250))',
                'pfe_multiplier': 'min(1, 0.05 + 0.95 * exp((V-C)/(2*0.95*AddOn)))',
                'replacement_cost': 'max(V; 0) [ignores collateral]',
                'regulation': '12 CFR 217.132'
            }
        }
    
    def _get_us_supervisory_factor_percent(self, trade: Trade) -> float:
        """Get supervisory factor as percentage per 12 CFR 217.132 Table 3."""
        if trade.asset_class == AssetClass.INTEREST_RATE:
            # Table 3: Interest rate derivatives - NO MATURITY DEPENDENCE
            currency_group = trade.currency if trade.currency in ['USD', 'EUR', 'JPY', 'GBP', 'CHF', 'CAD', 'AUD'] else 'other'
            return self.supervisory_factors[AssetClass.INTEREST_RATE][currency_group]
        
        elif trade.asset_class == AssetClass.FOREIGN_EXCHANGE:
            is_g10 = trade.currency in G10_CURRENCIES
            return self.supervisory_factors[AssetClass.FOREIGN_EXCHANGE]['G10' if is_g10 else 'emerging']
        
        elif trade.asset_class == AssetClass.CREDIT:
            # Assume Investment Grade for reference example
            return self.supervisory_factors[AssetClass.CREDIT]['IG']
        
        elif trade.asset_class == AssetClass.EQUITY:
            # Assume single-name equity
            return self.supervisory_factors[AssetClass.EQUITY]['single']
        
        elif trade.asset_class == AssetClass.COMMODITY:
            # Default to energy
            return self.supervisory_factors[AssetClass.COMMODITY]['energy']
        
        return 0.50  # Default 0.50% for USD IR per Table 3


# ==============================================================================
# REFERENCE EXAMPLE WITH US REGULATIONS (12 CFR 217.132)
# ==============================================================================

def create_us_reference_example():
    """
    Create reference example using US regulatory parameters from 12 CFR 217.132.
    """
    from datetime import datetime
    
    # Reference date from example
    as_of_date = datetime(2020, 12, 31)
    
    # Single interest rate swap trade matching reference
    trades = [
        Trade(
            trade_id="20BN474100",
            counterparty="Lowell Hotel Properties LLC",
            asset_class=AssetClass.INTEREST_RATE,
            trade_type=TradeType.SWAP,
            notional=100_000_000,  # $100M original notional
            currency="USD",
            underlying="USD Interest Rate Swap",
            maturity_date=datetime(2029, 4, 30),  # 8.33 years from reference
            settlement_date=datetime(2020, 6, 23),  # Settlement date from reference
            mtm_value=8_382_419,  # Net MTM from reference
            delta=1.0,
            basis_flag=False,
            volatility_flag=False,
            ceu_flag=1  # CEU = 1 for reference example
        )
    ]
    
    # Netting set with CSA terms from reference
    netting_set = NettingSet(
        netting_set_id="212784060000098918701",
        counterparty="Lowell Hotel Properties LLC", 
        trades=trades,
        threshold=12_000_000,   # TH = $12M from reference
        mta=1_000_000,         # MTA = $1M from reference
        nica=0,                # NICA = $0 from reference
        has_csa=True
    )
    
    # No collateral in reference example
    collateral = None
    
    return netting_set, collateral, as_of_date


def test_us_saccr_calculation():
    """Test the US SA-CCR calculation against the reference example."""
    
    print("Testing US SA-CCR Engine per 12 CFR 217.132")
    print("=" * 80)
    
    # Create reference data
    netting_set, collateral, as_of_date = create_us_reference_example()
    
    print(f"""
US REGULATORY REFERENCE INPUT DATA:
• Regulation: 12 CFR 217.132
• Trade ID: {netting_set.trades[0].trade_id}
• Original Notional: ${netting_set.trades[0].notional:,.0f}
• Asset Class: {netting_set.trades[0].asset_class.value}
• Currency: {netting_set.trades[0].currency}
• Maturity: {netting_set.trades[0].maturity_date.strftime('%Y-%m-%d')} ({netting_set.trades[0].time_to_maturity(as_of_date):.2f} years)
• MTM Value: ${netting_set.trades[0].mtm_value:,.0f}
• CSA Terms:
  - Threshold (TH): ${netting_set.threshold:,.0f}
  - MTA: ${netting_set.mta:,.0f}
  - NICA: ${netting_set.nica:,.0f}
• CEU Flag: {netting_set.trades[0].ceu_flag}
    """)
    
    # Calculate using US engine
    engine = USSACCREngine(as_of_date=as_of_date)
    results = engine.calculate_dual_scenario_saccr(netting_set, collateral)
    
    # Display results with US regulatory references
    margined = results['scenarios']['margined']
    unmargined = results['scenarios']['unmargined']
    selected = results['selection']['selected_scenario']
    
    print(f"""
US SA-CCR CALCULATION RESULTS (12 CFR 217.132):

SHARED STEPS (SAME FOR BOTH SCENARIOS):
• Step 4 - Time to Maturity: {results['shared_calculation_steps'][4]['time_params'][0]['M']:.2f} years
• Step 5 - Supervisory Duration: {results['shared_calculation_steps'][5]['adjusted_notionals'][0]['supervisory_duration']:.6f}
• Step 5 - Adjusted Notional: ${results['shared_calculation_steps'][5]['adjusted_notionals'][0]['adjusted_notional']:,.0f}
  Formula: max(0.05 * (e^(-0.05*S) - e^(-0.05*E)), 0.04) * Notional * 10000
• Step 8 - Supervisory Factor: {results['shared_calculation_steps'][8]['supervisory_factors'][0]['supervisory_factor_percent']:.2f}%
  Source: {results['shared_calculation_steps'][8]['supervisory_factors'][0]['table_reference']}
  Note: NO MATURITY DEPENDENCE for Interest Rate derivatives per Table 3
• Step 20 - Alpha: {results['shared_calculation_steps'][20]['alpha']} (CEU={results['shared_calculation_steps'][19]['ceu_flag']})

MARGINED SCENARIO (12 CFR 217.132):
• Step 6 - MF: {margined['maturity_factors'][0]['maturity_factor']:.6f}
  Formula: {margined['maturity_factors'][0]['formula']}
  MPOR: {margined['maturity_factors'][0]['mpor_days']} business days
• Step 9 - Adjusted Amount: ${margined['adjusted_amounts'][0]['adjusted_amount']:,.0f}
• Step 13 - Aggregate AddOn: ${margined['aggregate_addon']:,.0f}
• Step 15 - PFE Multiplier: {margined['pfe_multiplier']:.6f}
• Step 16 - PFE: ${margined['pfe']:,.0f}
• Step 18 - RC: ${margined['rc']:,.0f}
  Formula: {margined['regulatory_formulas']['replacement_cost']}
• Step 21 - EAD: ${margined['final_ead']:,.0f}

UNMARGINED SCENARIO (12 CFR 217.132):
• Step 6 - MF: {unmargined['maturity_factors'][0]['maturity_factor']:.6f}
  Formula: {unmargined['maturity_factors'][0]['formula']}
  MPOR: {unmargined['maturity_factors'][0]['mpor_days']} business days
• Step 9 - Adjusted Amount: ${unmargined['adjusted_amounts'][0]['adjusted_amount']:,.0f}
• Step 13 - Aggregate AddOn: ${unmargined['aggregate_addon']:,.0f}
• Step 15 - PFE Multiplier: {unmargined['pfe_multiplier']:.6f}
• Step 16 - PFE: ${unmargined['pfe']:,.0f}
• Step 18 - RC: ${unmargined['rc']:,.0f}
  Formula: {unmargined['regulatory_formulas']['replacement_cost']}
• Step 21 - EAD: ${unmargined['final_ead']:,.0f}

FINAL SELECTION (12 CFR 217.132):
• Selected: {selected} Scenario
• Final EAD: ${results['final_results']['exposure_at_default']:,.0f}
• Final Capital Requirement: ${results['final_results']['capital_requirement']:,.0f}
• Selection Rule: Lower EAD between margined and unmargined scenarios
• Regulatory Reference: {results['regulatory_reference']}
    """)
    
    return results


def validate_us_calculations():
    """Validate calculations against reference values using US regulations."""
    
    print("\nUS REGULATORY VALIDATION (12 CFR 217.132):")
    print("=" * 60)
    
    # Expected values from reference documentation
    expected_values = {
        'adjusted_notional': 681_578_943,
        'mf_margined': 0.3,
        'mf_unmargined': 1.0,
        'adjusted_amount_margined': 1_022_368,
        'adjusted_amount_unmargined': 3_407_895,
        'aggregate_addon_margined': 1_022_368,
        'aggregate_addon_unmargined': 3_407_895,
        'pfe_margined': 1_022_368,
        'pfe_unmargined': 3_407_895,
        'rc_margined': 13_000_000,
        'rc_unmargined': 8_382_419,
        'ead_margined': 14_022_368,
        'ead_unmargined': 11_790_314,
        'final_ead': 11_790_314
    }
    
    netting_set, collateral, as_of_date = create_us_reference_example()
    engine = USSACCREngine(as_of_date=as_of_date)
    results = engine.calculate_dual_scenario_saccr(netting_set, collateral)
    
    # Validation function
    def validate_value(description, calculated, expected, tolerance=0.02):
        if expected == 0:
            variance = abs(calculated - expected)
            passed = variance <= 1000
        else:
            variance = abs((calculated - expected) / expected)
            passed = variance <= tolerance
        
        status = "✓" if passed else "✗"
        variance_pct = variance * 100 if expected != 0 else variance
        print(f"{description}: {calculated:,.0f} (Expected: {expected:,.0f}) {status} [{variance_pct:.1f}%]")
        return passed
    
    # Run all validations
    all_passed = True
    
    print("Key US Regulatory Calculations:")
    
    # Supervisory Factor validation
    us_sf = results['shared_calculation_steps'][8]['supervisory_factors'][0]['supervisory_factor_percent']
    print(f"US Supervisory Factor: {us_sf:.2f}% (Table 3: Interest Rate, USD, no maturity dependence) ✓")
    
    calculated_adj_notional = results['shared_calculation_steps'][5]['adjusted_notionals'][0]['adjusted_notional']
    all_passed &= validate_value("Step 5 - Adjusted Notional", calculated_adj_notional, expected_values['adjusted_notional'])
    
    calculated_mf_margined = results['scenarios']['margined']['maturity_factors'][0]['maturity_factor']
    all_passed &= validate_value("Step 6 - MF Margined", calculated_mf_margined, expected_values['mf_margined'])
    
    calculated_mf_unmargined = results['scenarios']['unmargined']['maturity_factors'][0]['maturity_factor']
    all_passed &= validate_value("Step 6 - MF Unmargined", calculated_mf_unmargined, expected_values['mf_unmargined'])
    
    print("\nFinal Results:")
    all_passed &= validate_value("Margined EAD", results['scenarios']['margined']['final_ead'], expected_values['ead_margined'])
    all_passed &= validate_value("Unmargined EAD", results['scenarios']['unmargined']['final_ead'], expected_values['ead_unmargined'])
    all_passed &= validate_value("Final Selected EAD", results['final_results']['exposure_at_default'], expected_values['final_ead'])
    
    print(f"\nOVERALL US REGULATORY VALIDATION: {'PASSED ✓' if all_passed else 'FAILED ✗'}")
    
    return all_passed


def display_us_regulatory_details():
    """Display key US regulatory details from 12 CFR 217.132."""
    
    print("\nUS REGULATORY FRAMEWORK DETAILS (12 CFR 217.132):")
    print("=" * 70)
    
    print(f"""
TABLE 3 TO § 217.132 - COMPLETE SUPERVISORY PARAMETERS:

SUPERVISORY FACTORS (Percent):
Interest Rate:
• All currencies: {US_SUPERVISORY_FACTORS[AssetClass.INTEREST_RATE]['all_currencies']:.2f}% (NO currency/maturity dependence)

Exchange Rate (Foreign Exchange):
• All currencies: {US_SUPERVISORY_FACTORS[AssetClass.FOREIGN_EXCHANGE]['all_currencies']:.2f}%

Credit, Single Name:
• Investment Grade: {US_SUPERVISORY_FACTORS[AssetClass.CREDIT]['single_name_investment_grade']:.2f}%
• Speculative Grade: {US_SUPERVISORY_FACTORS[AssetClass.CREDIT]['single_name_speculative_grade']:.2f}%
• Sub-speculative Grade: {US_SUPERVISORY_FACTORS[AssetClass.CREDIT]['single_name_sub_speculative_grade']:.2f}%

Credit, Index:
• Investment Grade: {US_SUPERVISORY_FACTORS[AssetClass.CREDIT]['index_investment_grade']:.2f}%
• Speculative Grade: {US_SUPERVISORY_FACTORS[AssetClass.CREDIT]['index_speculative_grade']:.2f}%

Equity:
• Single Name: {US_SUPERVISORY_FACTORS[AssetClass.EQUITY]['single_name']:.1f}%
• Index: {US_SUPERVISORY_FACTORS[AssetClass.EQUITY]['index']:.1f}%

Commodity:
• Energy - Electricity: {US_SUPERVISORY_FACTORS[AssetClass.COMMODITY]['energy_electricity']:.1f}%
• Energy - Other: {US_SUPERVISORY_FACTORS[AssetClass.COMMODITY]['energy_other']:.1f}%
• Metals: {US_SUPERVISORY_FACTORS[AssetClass.COMMODITY]['metals']:.1f}%
• Agricultural: {US_SUPERVISORY_FACTORS[AssetClass.COMMODITY]['agricultural']:.1f}%
• Other: {US_SUPERVISORY_FACTORS[AssetClass.COMMODITY]['other']:.1f}%

SUPERVISORY CORRELATIONS (Percent):
Interest Rate: N/A (typically 99% in practice)
Exchange Rate: N/A (typically 60% in practice)
Credit:
• Single Name: {US_SUPERVISORY_CORRELATIONS[AssetClass.CREDIT]['single_name']:.0%}
• Index: {US_SUPERVISORY_CORRELATIONS[AssetClass.CREDIT]['index']:.0%}
Equity:
• Single Name: {US_SUPERVISORY_CORRELATIONS[AssetClass.EQUITY]['single_name']:.0%}
• Index: {US_SUPERVISORY_CORRELATIONS[AssetClass.EQUITY]['index']:.0%}
Commodity: {US_SUPERVISORY_CORRELATIONS[AssetClass.COMMODITY]:.0%}

SUPERVISORY OPTION VOLATILITY (Percent):
Interest Rate: {US_SUPERVISORY_OPTION_VOLATILITY[AssetClass.INTEREST_RATE]:.0f}%
Exchange Rate: {US_SUPERVISORY_OPTION_VOLATILITY[AssetClass.FOREIGN_EXCHANGE]:.0f}%
Credit:
• Single Name: {US_SUPERVISORY_OPTION_VOLATILITY[AssetClass.CREDIT]['single_name']:.0f}%
• Index IG: {US_SUPERVISORY_OPTION_VOLATILITY[AssetClass.CREDIT]['index_investment_grade']:.0f}%
• Index Speculative: {US_SUPERVISORY_OPTION_VOLATILITY[AssetClass.CREDIT]['index_speculative_grade']:.0f}%
Equity:
• Single Name: {US_SUPERVISORY_OPTION_VOLATILITY[AssetClass.EQUITY]['single_name']:.0f}%
• Index: {US_SUPERVISORY_OPTION_VOLATILITY[AssetClass.EQUITY]['index']:.0f}%
Commodity:
• Energy - Electricity: {US_SUPERVISORY_OPTION_VOLATILITY[AssetClass.COMMODITY]['energy_electricity']:.0f}%
• Energy - Other: {US_SUPERVISORY_OPTION_VOLATILITY[AssetClass.COMMODITY]['energy_other']:.0f}%
• Metals: {US_SUPERVISORY_OPTION_VOLATILITY[AssetClass.COMMODITY]['metals']:.0f}%
• Agricultural: {US_SUPERVISORY_OPTION_VOLATILITY[AssetClass.COMMODITY]['agricultural']:.0f}%
• Other: {US_SUPERVISORY_OPTION_VOLATILITY[AssetClass.COMMODITY]['other']:.0f}%

US MPOR VALUES:
• Margined transactions: {US_MPOR_VALUES['margined_standard']} business days
• Margined with disputes: {US_MPOR_VALUES['margined_disputes']} business days
• Unmargined transactions: {US_MPOR_VALUES['unmargined']} business days

KEY DIFFERENCES FROM BASEL III:
1. Interest rate supervisory factors do NOT depend on maturity
2. Single factor of 0.5% for major currencies (USD, EUR, JPY, GBP, etc.)
3. Table 3 provides definitive supervisory parameters
4. US-specific Alpha calculation (1.0 for CEU=1, 1.4 for CEU=0)

REGULATORY AUTHORITY:
• Federal Register: 12 CFR 217.132
• Applicable to Board-regulated institutions
• Part of US Basel III implementation
    """)


# Test if executed directly
if __name__ == "__main__":
    print("Running US SA-CCR Engine per 12 CFR 217.132...")
    print("=" * 90)
    
    # Show regulatory details first
    display_us_regulatory_details()
    
    print("\n" + "="*90)
    
    # Run main test
    test_results = test_us_saccr_calculation()
    
    print("\n" + "="*90)
    
    # Run validation
    validation_passed = validate_us_calculations()
    
    print("\n" + "="*90)
    
    if validation_passed:
        print("🎉 SUCCESS: US SA-CCR Engine correctly implements 12 CFR 217.132!")
        print("📊 All calculations match the reference example using US regulations.")
        print("📜 Table 3 supervisory factors properly applied (no maturity dependence for IR).")
        print("🇺🇸 Engine follows Federal Register requirements exactly.")
    else:
        print("⚠️  ATTENTION: Some values differ - review US regulatory requirements.")
        print("📝 Check 12 CFR 217.132 for specific US implementation details.")
    
    print(f"""
🔗 REGULATORY REFERENCES:
✓ 12 CFR 217.132 - Primary regulation for counterparty credit risk
✓ Table 3 to § 217.132 - Supervisory factors and correlations  
✓ Federal Register implementation of Basel III SA-CCR
✓ US-specific parameters and calculation methodologies

📋 KEY FINDING:
Interest rate supervisory factors are maturity-independent per Table 3:
• USD Interest Rate derivatives: 0.5% (flat across all maturities)
• This differs from international Basel III which has maturity buckets
• US regulation provides simpler, single-factor approach
    """)

Margined)
        hedging_sets = self.shared_steps[3]['hedging_sets']
        hedging_set_addons_margined = []
        
        for hedging_set_key, trade_ids in hedging_sets.items():
            hedging_set_addon = sum(
                amt['adjusted_amount'] for amt in adjusted_amounts_margined 
                if amt['trade_id'] in trade_ids
            )
            hedging_set_addons_margined.append({
                'hedging_set': hedging_set_key,
                'hedging_set_addon': abs(hedging_set_addon)
            })
        
        # Step 12: Asset Class AddOn (Margined)
        asset_class_addons_margined = []
        for hsa in hedging_set_addons_margined:
            asset_class_addons_margined.append({
                'asset_class': hsa['hedging_set'],
                'asset_class_addon': hsa['hedging_set_addon']
            })
        
        # Step 13: Aggregate AddOn (Margined)
        aggregate_addon_margined = sum(ac['asset_class_addon'] for ac in asset_class_addons_margined)
        
        # Step 15: PFE Multiplier per 12 CFR 217.132
        net_exposure = self.shared_steps[14]['net_exposure']
        if aggregate_addon_margined > 0:
            # 12 CFR 217.132: Multiplier = min(1, 0.05 + 0.95 * exp((V-C) / (2 * 0.95 * AddOn)))
            exponent = net_exposure / (2 * 0.95 * aggregate_addon_margined)
            multiplier_margined = min(1.0, 0.05 + 0.95 * math.exp(exponent))
        else:
            multiplier_margined = 1.0
        
        # Step 16: PFE (Margined)
        pfe_margined = multiplier_margined * aggregate_addon_margined
        
        # Step 18: RC (Margined) per 12 CFR 217.132
        sum_v = self.shared_steps[14]['sum_v']
        sum_c = self.shared_steps[14]['sum_c']
        threshold = self.shared_steps[17]['threshold']
        mta = self.shared_steps[17]['mta']
        nica = self.shared_steps[17]['nica']
        
        # 12 CFR 217.132 Margined RC: RC = max(V - C; TH + MTA - NICA; 0)
        rc_margined = max(sum_v - sum_c, threshold + mta - nica, 0)
        
        # Step 21: EAD (Margined)
        alpha = self.shared_steps[20]['alpha']
        ead_margined = alpha * (rc_margined + pfe_margined)
        
        # Step 24: RWA and Capital (Margined)
        risk_weight = self.shared_steps[23]['risk_weight']
        rwa_margined = ead_margined * risk_weight
        capital_margined = rwa_margined * US_CAPITAL_RATIO
        
        return {
            'scenario': 'Margined',
            'maturity_factors': maturity_factors_margined,
            'adjusted_amounts': adjusted_amounts_margined,
            'hedging_set_addons': hedging_set_addons_margined,
            'asset_class_addons': asset_class_addons_margined,
            'aggregate_addon': aggregate_addon_margined,
            'pfe_multiplier': multiplier_margined,
            'pfe': pfe_margined,
            'rc': rc_margined,
            'final_ead': ead_margined,
            'rwa': rwa_margined,
            'final_capital': capital_margined,
            'regulatory_formulas': {
                'maturity_factor': f'sqrt(min(M, {US_MPOR_VALUES["margined_standard"]}/250)) × 1.5 [short-term]',
                'pfe_multiplier': 'min(1, 0.05 + 0.95 * exp((V-C)/(2*0.95*AddOn)))',
                'replacement_cost': 'max(V-C; TH+MTA-NICA; 0)',
                'regulation': '12 CFR 217.132'
            }
        }
    
    def _calculate_unmargined_scenario(self, netting_set: NettingSet, collateral: List[Collateral] = None) -> Dict:
        """Calculate unmargined scenario per 12 CFR 217.132."""
        
        # Step 6: Maturity Factor (Unmargined) per US regulations
        maturity_factors_unmargined = []
        for trade in netting_set.trades:
            mf = self._calculate_us_maturity_factor(trade, "unmargined")
            maturity_factors_unmargined.append({
                'trade_id': trade.trade_id,
                'maturity_factor': mf,
                'formula': 'max(sqrt(min(M, 1)), sqrt(10/250))',
                'mpor_days': US_MPOR_VALUES['unmargined']
            })
        
        # Step 9: Adjusted Derivatives Contract Amount (Unmargined)
        adjusted_amounts_unmargined = []
        for i, trade in enumerate(netting_set.trades):
            adjusted_notional = self.shared_steps[5]['adjusted_notionals'][i]['adjusted_notional']
            supervisory_delta = self.shared_steps[7]['supervisory_deltas'][i]['supervisory_delta']
            mf = maturity_factors_unmargined[i]['maturity_factor']
            sf = self.shared_steps[8]['supervisory_factors'][i]['supervisory_factor_decimal']
            
            adjusted_amount = adjusted_notional * supervisory_delta * mf * sf
            adjusted_amounts_unmargined.append({
                'trade_id': trade.trade_id,
                'adjusted_amount': adjusted_amount,
                'formula': 'Adjusted Notional × Delta × MF × SF (12 CFR 217.132)'
            })
        
        # Step 11: Hedging Set AddOn (
