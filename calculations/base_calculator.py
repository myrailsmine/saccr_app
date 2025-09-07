from abc import ABC, abstractmethod
from typing import Dict, List, Any
from models.netting_set import NettingSet
from models.collateral import Collateral

class BaseCalculator(ABC):
    """Abstract base class for SA-CCR calculators."""
    
    @abstractmethod
    def calculate(self, netting_set: NettingSet, 
                 collateral: List[Collateral] = None) -> Dict[str, Any]:
        """Main calculation method."""
        pass
    
    @abstractmethod
    def validate_inputs(self, netting_set: NettingSet, 
                       collateral: List[Collateral] = None) -> Dict[str, Any]:
        """Validate calculation inputs."""
        pass

class CalculationStep:
    """Represents a single calculation step in SA-CCR."""
    
    def __init__(self, step_number: int, title: str, description: str):
        self.step_number = step_number
        self.title = title
        self.description = description
        self.data = {}
        self.formula = ""
        self.result = ""
        self.thinking = {}
    
    def set_result(self, data: Dict, formula: str, result: str):
        """Set calculation results."""
        self.data = data
        self.formula = formula
        self.result = result
    
    def add_thinking(self, reasoning: str, key_insight: str = ""):
        """Add thinking process information."""
        self.thinking = {
            'step': self.step_number,
            'title': f"{self.title} Analysis",
            'reasoning': reasoning,
            'formula': self.formula,
            'key_insight': key_insight
        }
