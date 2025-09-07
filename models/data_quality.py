# models/data_quality.py
"""Data quality issue tracking."""

from dataclasses import dataclass
from typing import Any, Optional
from models.enums import DataQualityIssueType, DataQualityImpact

@dataclass
class DataQualityIssue:
    """Represents a data quality issue in the calculation."""
    field_name: str
    current_value: Any
    issue_type: DataQualityIssueType
    impact: DataQualityImpact
    recommendation: str
    default_used: Optional[Any] = None
    
    def is_high_impact(self) -> bool:
        """Check if this is a high impact issue."""
        return self.impact == DataQualityImpact.HIGH
