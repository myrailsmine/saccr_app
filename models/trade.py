# models/trade.py
"""Enhanced trade data model with comprehensive SA-CCR business logic."""

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from models.enums import AssetClass, TradeType

@dataclass
class Trade:
    """
    Enhanced trade model implementing complete Basel SA-CCR methodology.
    
    Supports all asset classes, trade types, and calculation requirements
    per Basel III SA-CCR framework and US 12 CFR 217.132.
    """
    # Core trade identification
    trade_id: str
    counterparty: str
    asset_class: AssetClass
    trade_type: TradeType
    notional: float
    currency: str
    underlying: str
    maturity_date: datetime
    
    # Market and risk data
    mtm_value: float = 0.0
    delta: float = 1.0
    settlement_date: Optional[datetime] = None
    
    # SA-CCR specific flags and parameters
    basis_flag: bool = False
    volatility_flag: bool = False
    ceu_flag: int = 1  # Central clearing flag (1 = centrally cleared, 0 = bilateral)
    
    # Additional trade characteristics for SA-CCR
    credit_quality: str = "investment_grade"  # For credit derivatives
    reference_entity: str = ""  # For credit single name
    index_name: str = ""  # For index derivatives
    commodity_type: str = "energy_other"  # For commodity derivatives
    equity_type: str = "single_name"  # For equity derivatives
    
    # Option-specific parameters
    option_strike: Optional[float] = None
    option_type: str = "call"  # call, put
    barrier_type: Optional[str] = None  # For barrier options
    
    # Interest rate specific
    fixed_rate: Optional[float] = None
    floating_reference: str = ""  # e.g., "USD-LIBOR-3M"
    payment_frequency: str = "quarterly"
    
    # Computed fields (auto-calculated)
    _hedging_set_key: Optional[str] = field(default=None, init=False)
    _supervisory_duration: Optional[float] = field(default=None, init=False)
    _time_params: Optional[Dict[str, float]] = field(default=None, init=False)
    
    def __post_init__(self):
        """Initialize computed fields after object creation."""
        if self.settlement_date is None:
            # Default settlement date to trade date + 2 business days
            self.settlement_date = datetime.now() + timedelta(days=2)
        
        # Pre-calculate hedging set key
        self._hedging_set_key = self._calculate_hedging_set_key()
    
    # ==================================================================================
    # TIME AND MATURITY CALCULATIONS
    # ==================================================================================
    
    def time_to_maturity(self, as_of_date: Optional[datetime] = None) -> float:
        """
        Calculate time to maturity in years from as_of_date.
        
        Args:
            as_of_date: Reference date (defaults to current date)
            
        Returns:
            Time to maturity in years (minimum 0)
        """
        if as_of_date is None:
            as_of_date = datetime.now()
        return max(0, (self.maturity_date - as_of_date).days / 365.25)
    
    def time_to_settlement(self, as_of_date: Optional[datetime] = None) -> float:
        """
        Calculate time to settlement in years from as_of_date.
        
        Args:
            as_of_date: Reference date (defaults to current date)
            
        Returns:
            Time to settlement in years (minimum 0)
        """
        if as_of_date is None:
            as_of_date = datetime.now()
        if self.settlement_date is None:
            return 0
        return max(0, (self.settlement_date - as_of_date).days / 365.25)
    
    def get_time_parameters(self, as_of_date: Optional[datetime] = None) -> Dict[str, float]:
        """
        Calculate S, E, M time parameters per Basel SA-CCR methodology.
        
        Args:
            as_of_date: Reference date
            
        Returns:
            Dictionary with S (settlement), E (end), M (maturity) parameters
        """
        if self._time_params is None or as_of_date is not None:
            S = self.time_to_settlement(as_of_date)
            M = self.time_to_maturity(as_of_date)
            
            # E (effective time) depends on trade type
            if self.trade_type in [TradeType.OPTION, TradeType.SWAPTION]:
                # For options, E is typically the option expiry
                E = M
            else:
                # For vanilla swaps and forwards, E = M
                E = M
            
            self._time_params = {"S": S, "E": E, "M": M}
        
        return self._time_params
    
    def get_maturity_bucket(self) -> str:
        """
        Get maturity bucket for supervisory factor lookup.
        
        Returns:
            Maturity bucket string ("<2y", "2-5y", ">5y")
        """
        maturity = self.time_to_maturity()
        if maturity < 2:
            return "<2y"
        elif maturity <= 5:
            return "2-5y"
        else:
            return ">5y"
    
    # ==================================================================================
    # SUPERVISORY DURATION AND ADJUSTED NOTIONAL
    # ==================================================================================
    
    def calculate_supervisory_duration(self, as_of_date: Optional[datetime] = None) -> float:
        """
        Calculate supervisory duration per Basel SA-CCR methodology.
        
        For interest rate derivatives only. Other asset classes use duration = 1.0.
        
        Args:
            as_of_date: Reference date
            
        Returns:
            Supervisory duration value
        """
        if self._supervisory_duration is None or as_of_date is not None:
            if self.asset_class == AssetClass.INTEREST_RATE:
                time_params = self.get_time_parameters(as_of_date)
                S = time_params["S"]
                E = time_params["E"]
                
                # Basel formula: SD = max(0.05 * (exp(-0.05*S) - exp(-0.05*E)), 0.04)
                exponential_term = math.exp(-0.05 * S) - math.exp(-0.05 * E)
                self._supervisory_duration = max(0.05 * exponential_term, 0.04)
            else:
                # Non-interest rate derivatives use duration = 1.0
                self._supervisory_duration = 1.0
        
        return self._supervisory_duration
    
    def calculate_adjusted_notional(self, as_of_date: Optional[datetime] = None) -> float:
        """
        Calculate adjusted notional amount per Basel SA-CCR methodology.
        
        Args:
            as_of_date: Reference date
            
        Returns:
            Adjusted notional amount
        """
        base_notional = abs(self.notional)
        
        if self.asset_class == AssetClass.INTEREST_RATE:
            # Interest rate: Adjusted Notional = |Notional| × SD × 10,000
            sd = self.calculate_supervisory_duration(as_of_date)
            return base_notional * sd * 10000
        else:
            # Other asset classes: Adjusted Notional = |Notional|
            return base_notional
    
    # ==================================================================================
    # HEDGING SET DETERMINATION
    # ==================================================================================
    
    def _calculate_hedging_set_key(self) -> str:
        """
        Calculate hedging set key per Basel SA-CCR methodology.
        
        Returns:
            Hedging set identifier string
        """
        if self.asset_class == AssetClass.INTEREST_RATE:
            # Interest rate: Hedging set = currency
            return f"IR_{self.currency}"
        
        elif self.asset_class == AssetClass.FOREIGN_EXCHANGE:
            # FX: Hedging set = currency pair (sorted alphabetically)
            currencies = sorted([self.currency, "USD"])  # Assuming USD as base
            return f"FX_{'_'.join(currencies)}"
        
        elif self.asset_class == AssetClass.CREDIT:
            # Credit: Hedging set = currency + quality + type
            if self.reference_entity:
                return f"CREDIT_{self.currency}_{self.credit_quality}_SINGLE_{self.reference_entity}"
            elif self.index_name:
                return f"CREDIT_{self.currency}_{self.credit_quality}_INDEX_{self.index_name}"
            else:
                return f"CREDIT_{self.currency}_{self.credit_quality}_SINGLE_UNKNOWN"
        
        elif self.asset_class == AssetClass.EQUITY:
            # Equity: Hedging set = currency + type + underlying
            equity_key = self.index_name if self.equity_type == "index" else self.underlying
            return f"EQUITY_{self.currency}_{self.equity_type}_{equity_key}"
        
        elif self.asset_class == AssetClass.COMMODITY:
            # Commodity: Hedging set = commodity type + underlying
            return f"COMMODITY_{self.commodity_type}_{self.underlying}"
        
        else:
            # Default case
            return f"{self.asset_class.value}_{self.currency}_{self.underlying}"
    
    def get_hedging_set_key(self) -> str:
        """
        Get hedging set key for the trade.
        
        Returns:
            Hedging set identifier
        """
        return self._hedging_set_key
    
    # ==================================================================================
    # DELTA AND OPTION CALCULATIONS
    # ==================================================================================
    
    def is_option_like(self) -> bool:
        """
        Check if trade is option-like.
        
        Returns:
            True if trade has option characteristics
        """
        return self.trade_type in [TradeType.OPTION, TradeType.SWAPTION]
    
    def get_supervisory_delta(self) -> float:
        """
        Calculate supervisory delta per Basel SA-CCR methodology.
        
        Returns:
            Supervisory delta value
        """
        if self.is_option_like():
            # Use provided delta for options
            return self.delta
        else:
            # For linear trades: +1 for long, -1 for short
            return 1.0 if self.notional > 0 else -1.0
    
    def calculate_option_adjusted_notional(self, volatility: float) -> float:
        """
        Calculate option-adjusted notional per Basel methodology.
        
        Args:
            volatility: Supervisory option volatility
            
        Returns:
            Option-adjusted notional
        """
        if not self.is_option_like():
            return self.calculate_adjusted_notional()
        
        # Simplified option adjustment formula
        # In practice, this would involve Black-Scholes calculations
        base_notional = self.calculate_adjusted_notional()
        vol_adjustment = 1.0 + (volatility / 100) * math.sqrt(self.time_to_maturity())
        return base_notional * vol_adjustment
    
    # ==================================================================================
    # ASSET CLASS SPECIFIC METHODS
    # ==================================================================================
    
    def get_credit_subcategory(self) -> str:
        """
        Get credit derivative subcategory for supervisory factor lookup.
        
        Returns:
            Credit subcategory string
        """
        if self.index_name:
            return f"index_{self.credit_quality}"
        else:
            return f"single_name_{self.credit_quality}"
    
    def get_commodity_subcategory(self) -> str:
        """
        Get commodity derivative subcategory for supervisory factor lookup.
        
        Returns:
            Commodity subcategory string
        """
        return self.commodity_type
    
    def get_equity_subcategory(self) -> str:
        """
        Get equity derivative subcategory for supervisory factor lookup.
        
        Returns:
            Equity subcategory string
        """
        return self.equity_type
    
    # ==================================================================================
    # VALIDATION AND COMPLETENESS
    # ==================================================================================
    
    def validate_completeness(self) -> Dict[str, Any]:
        """
        Validate trade data completeness for SA-CCR calculation.
        
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Required fields validation
        if not self.trade_id:
            errors.append("Trade ID is required")
        if not self.counterparty:
            errors.append("Counterparty is required")
        if self.notional == 0:
            errors.append("Notional amount cannot be zero")
        if not self.currency:
            errors.append("Currency is required")
        if not self.underlying:
            errors.append("Underlying is required")
        
        # Asset class specific validation
        if self.asset_class == AssetClass.CREDIT:
            if not self.reference_entity and not self.index_name:
                warnings.append("Credit trades should specify reference entity or index name")
        
        elif self.asset_class == AssetClass.COMMODITY:
            if self.commodity_type not in ["energy_electricity", "energy_other", "metals", "agricultural", "other"]:
                warnings.append(f"Unknown commodity type: {self.commodity_type}")
        
        elif self.asset_class == AssetClass.EQUITY:
            if self.equity_type not in ["single_name", "index"]:
                warnings.append(f"Equity type should be 'single_name' or 'index': {self.equity_type}")
        
        # Option validation
        if self.is_option_like():
            if self.option_strike is None:
                warnings.append("Option trades should specify strike price")
            if abs(self.delta) > 1.0:
                warnings.append("Option delta should be between -1 and 1")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'completeness_score': max(0, 1.0 - len(warnings) * 0.1)
        }
    
    # ==================================================================================
    # UTILITY AND DISPLAY METHODS
    # ==================================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert trade to dictionary for serialization.
        
        Returns:
            Trade data as dictionary
        """
        return {
            'trade_id': self.trade_id,
            'counterparty': self.counterparty,
            'asset_class': self.asset_class.value,
            'trade_type': self.trade_type.value,
            'notional': self.notional,
            'currency': self.currency,
            'underlying': self.underlying,
            'maturity_date': self.maturity_date.isoformat(),
            'mtm_value': self.mtm_value,
            'delta': self.delta,
            'time_to_maturity': self.time_to_maturity(),
            'hedging_set': self.get_hedging_set_key(),
            'adjusted_notional': self.calculate_adjusted_notional(),
            'supervisory_delta': self.get_supervisory_delta()
        }
    
    def get_display_summary(self) -> str:
        """
        Get formatted display summary of the trade.
        
        Returns:
            Formatted trade summary string
        """
        return f"""
Trade {self.trade_id}:
  • {self.asset_class.value} {self.trade_type.value}
  • Notional: ${self.notional:,.0f} {self.currency}
  • Underlying: {self.underlying}
  • Maturity: {self.maturity_date.strftime('%Y-%m-%d')} ({self.time_to_maturity():.1f}y)
  • MTM: ${self.mtm_value:,.0f}
  • Hedging Set: {self.get_hedging_set_key()}
        """.strip()
    
    def __str__(self) -> str:
        """String representation of the trade."""
        return f"Trade({self.trade_id}, {self.asset_class.value}, {self.notional:,.0f} {self.currency})"
    
    def __repr__(self) -> str:
        """Detailed representation of the trade."""
        return (f"Trade(trade_id='{self.trade_id}', asset_class={self.asset_class}, "
                f"notional={self.notional}, currency='{self.currency}', "
                f"maturity={self.maturity_date.strftime('%Y-%m-%d')})")

# ==================================================================================
# TRADE FACTORY AND HELPER FUNCTIONS
# ==================================================================================

class TradeFactory:
    """Factory class for creating specific types of trades."""
    
    @staticmethod
    def create_interest_rate_swap(
        trade_id: str,
        counterparty: str,
        notional: float,
        currency: str = "USD",
        maturity_years: float = 5.0,
        fixed_rate: float = 0.025,
        floating_reference: str = "USD-SOFR",
        mtm_value: float = 0.0
    ) -> Trade:
        """Create an interest rate swap trade."""
        return Trade(
            trade_id=trade_id,
            counterparty=counterparty,
            asset_class=AssetClass.INTEREST_RATE,
            trade_type=TradeType.SWAP,
            notional=notional,
            currency=currency,
            underlying=f"{currency} Interest Rate Swap",
            maturity_date=datetime.now() + timedelta(days=int(maturity_years * 365)),
            mtm_value=mtm_value,
            fixed_rate=fixed_rate,
            floating_reference=floating_reference
        )
    
    @staticmethod
    def create_fx_forward(
        trade_id: str,
        counterparty: str,
        notional: float,
        currency_pair: str = "EURUSD",
        maturity_days: int = 90,
        forward_rate: float = 1.1000,
        mtm_value: float = 0.0
    ) -> Trade:
        """Create an FX forward trade."""
        base_ccy = currency_pair[:3]
        return Trade(
            trade_id=trade_id,
            counterparty=counterparty,
            asset_class=AssetClass.FOREIGN_EXCHANGE,
            trade_type=TradeType.FORWARD,
            notional=notional,
            currency=base_ccy,
            underlying=currency_pair,
            maturity_date=datetime.now() + timedelta(days=maturity_days),
            mtm_value=mtm_value
        )
    
    @staticmethod
    def create_credit_default_swap(
        trade_id: str,
        counterparty: str,
        notional: float,
        reference_entity: str,
        currency: str = "USD",
        maturity_years: float = 5.0,
        credit_quality: str = "investment_grade",
        mtm_value: float = 0.0
    ) -> Trade:
        """Create a credit default swap trade."""
        return Trade(
            trade_id=trade_id,
            counterparty=counterparty,
            asset_class=AssetClass.CREDIT,
            trade_type=TradeType.SWAP,
            notional=notional,
            currency=currency,
            underlying=f"CDS on {reference_entity}",
            maturity_date=datetime.now() + timedelta(days=int(maturity_years * 365)),
            mtm_value=mtm_value,
            reference_entity=reference_entity,
            credit_quality=credit_quality
        )
    
    @staticmethod
    def create_equity_option(
        trade_id: str,
        counterparty: str,
        notional: float,
        underlying: str,
        currency: str = "USD",
        maturity_days: int = 30,
        option_type: str = "call",
        strike: float = 100.0,
        delta: float = 0.5,
        mtm_value: float = 0.0
    ) -> Trade:
        """Create an equity option trade."""
        return Trade(
            trade_id=trade_id,
            counterparty=counterparty,
            asset_class=AssetClass.EQUITY,
            trade_type=TradeType.OPTION,
            notional=notional,
            currency=currency,
            underlying=underlying,
            maturity_date=datetime.now() + timedelta(days=maturity_days),
            mtm_value=mtm_value,
            delta=delta,
            option_type=option_type,
            option_strike=strike,
            equity_type="single_name"
        )


def create_sample_trades() -> List[Trade]:
    """Create sample trades for testing and demonstration."""
    return [
        TradeFactory.create_interest_rate_swap(
            "IRS001", "Sample Bank", 100_000_000, "USD", 5.0
        ),
        TradeFactory.create_fx_forward(
            "FXF001", "Sample Bank", 50_000_000, "EURUSD", 90
        ),
        TradeFactory.create_credit_default_swap(
            "CDS001", "Sample Bank", 25_000_000, "Corporate XYZ"
        ),
        TradeFactory.create_equity_option(
            "EQO001", "Sample Bank", 10_000_000, "SPX Index", "USD", 30
        )
    ]
