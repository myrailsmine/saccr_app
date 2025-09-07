# ==============================================================================
# UTILS/DATA_EXPORT.PY - Data Export Utilities
# ==============================================================================

"""
Data export utilities for SA-CCR calculation results.
Handles CSV, Excel, JSON, and PDF export functionality with proper formatting.
"""

import json
import csv
import io
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import pandas as pd
from pathlib import Path

from config.settings import (
    EXPORT_CONFIG, FILE_NAMING, TABLE_CONFIG, APP_NAME, APP_VERSION
)


class SACCRDataExporter:
    """Main class for exporting SA-CCR calculation data in various formats."""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime(FILE_NAMING['timestamp_format'])
    
    def export_summary_csv(self, results: Dict[str, Any], 
                          netting_set_id: str = "unknown") -> str:
        """
        Export summary results to CSV format.
        
        Args:
            results: SA-CCR calculation results
            netting_set_id: Identifier for the netting set
            
        Returns:
            CSV data as string
        """
        summary_data = self._prepare_summary_data(results, netting_set_id)
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=summary_data.keys())
        writer.writeheader()
        writer.writerow(summary_data)
        
        return output.getvalue()
    
    def export_steps_csv(self, calculation_steps: List[Dict]) -> str:
        """
        Export detailed calculation steps to CSV format.
        
        Args:
            calculation_steps: List of calculation step results
            
        Returns:
            CSV data as string
        """
        steps_data = []
        for step in calculation_steps:
            step_row = {
                'Step': step.step,
                'Title': step.title,
                'Description': step.description,
                'Formula': step.formula,
                'Result': step.result
            }
            
            # Add key data points if available
            if hasattr(step, 'data') and isinstance(step.data, dict):
                for key, value in step.data.items():
                    if isinstance(value, (int, float, str)):
                        step_row[f'Data_{key}'] = value
            
            steps_data.append(step_row)
        
        if not steps_data:
            return "No calculation steps available"
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=steps_data[0].keys())
        writer.writeheader()
        writer.writerows(steps_data)
        
        return output.getvalue()
    
    def export_portfolio_csv(self, trades: List, collateral: List = None) -> str:
        """
        Export portfolio data to CSV format.
        
        Args:
            trades: List of Trade objects
            collateral: Optional list of Collateral objects
            
        Returns:
            CSV data as string
        """
        # Prepare trades data
        trades_data = []
        for trade in trades:
            trade_row = {
                'Trade_ID': trade.trade_id,
                'Counterparty': trade.counterparty,
                'Asset_Class': trade.asset_class.value,
                'Trade_Type': trade.trade_type.value,
                'Notional': trade.notional,
                'Currency': trade.currency,
                'Underlying': trade.underlying,
                'Maturity_Date': trade.maturity_date.strftime('%Y-%m-%d'),
                'Time_to_Maturity_Years': trade.time_to_maturity(),
                'MTM_Value': trade.mtm_value,
                'Delta': trade.delta,
                'CEU_Flag': getattr(trade, 'ceu_flag', 1)
            }
            trades_data.append(trade_row)
        
        output = io.StringIO()
        if trades_data:
            writer = csv.DictWriter(output, fieldnames=trades_data[0].keys())
            writer.writeheader()
            writer.writerows(trades_data)
        
        # Add collateral data if provided
        if collateral:
            output.write("\n\nCollateral Data:\n")
            collateral_data = []
            for coll in collateral:
                coll_row = {
                    'Collateral_Type': coll.collateral_type.value,
                    'Currency': coll.currency,
                    'Amount': coll.amount,
                    'Haircut': getattr(coll, 'haircut', 0)
                }
                collateral_data.append(coll_row)
            
            if collateral_data:
                writer = csv.DictWriter(output, fieldnames=collateral_data[0].keys())
                writer.writeheader()
                writer.writerows(collateral_data)
        
        return output.getvalue()
    
    def export_excel_workbook(self, results: Dict[str, Any], 
                             trades: List = None, collateral: List = None,
                             filename: str = None) -> bytes:
        """
        Export comprehensive results to Excel workbook.
        
        Args:
            results: SA-CCR calculation results
            trades: List of Trade objects
            collateral: List of Collateral objects
            filename: Optional filename
            
        Returns:
            Excel file as bytes
        """
        if filename is None:
            filename = f"saccr_analysis_{self.timestamp}.xlsx"
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = self._prepare_summary_data(results)
            summary_df = pd.DataFrame([summary_data])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Calculation steps sheet
            if results.get('calculation_steps'):
                steps_data = self._prepare_steps_dataframe(results['calculation_steps'])
                steps_data.to_excel(writer, sheet_name='Calculation_Steps', index=False)
            
            # Portfolio sheet
            if trades:
                portfolio_df = self._prepare_portfolio_dataframe(trades, collateral)
                portfolio_df.to_excel(writer, sheet_name='Portfolio', index=False)
            
            # Enhanced summary sheet
            if results.get('enhanced_summary'):
                enhanced_df = self._prepare_enhanced_summary_dataframe(results['enhanced_summary'])
                enhanced_df.to_excel(writer, sheet_name='Enhanced_Analysis', index=False)
            
            # Data quality sheet
            if results.get('data_quality_issues'):
                dq_df = self._prepare_data_quality_dataframe(results['data_quality_issues'])
                dq_df.to_excel(writer, sheet_name='Data_Quality', index=False)
        
        output.seek(0)
        return output.read()
    
    def export_json_complete(self, results: Dict[str, Any], 
                           include_metadata: bool = True) -> str:
        """
        Export complete results to JSON format.
        
        Args:
            results: SA-CCR calculation results
            include_metadata: Whether to include metadata
            
        Returns:
            JSON data as string
        """
        export_data = results.copy()
        
        if include_metadata:
            export_data['export_metadata'] = {
                'application': APP_NAME,
                'version': APP_VERSION,
                'export_timestamp': datetime.now().isoformat(),
                'export_format': 'JSON',
                'data_includes': list(results.keys())
            }
        
        # Convert non-serializable objects
        export_data = self._make_json_serializable(export_data)
        
        return json.dumps(export_data, indent=EXPORT_CONFIG['json_indent'], 
                         ensure_ascii=False, default=str)
    
    def _prepare_summary_data(self, results: Dict[str, Any], 
                             netting_set_id: str = "unknown") -> Dict[str, Any]:
        """Prepare summary data for export."""
        final_results = results.get('final_results', {})
        
        return {
            'Calculation_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Netting_Set_ID': netting_set_id,
            'Application': APP_NAME,
            'Version': APP_VERSION,
            'Replacement_Cost_USD': final_results.get('replacement_cost', 0),
            'Potential_Future_Exposure_USD': final_results.get('potential_future_exposure', 0),
            'Exposure_at_Default_USD': final_results.get('exposure_at_default', 0),
            'Risk_Weighted_Assets_USD': final_results.get('risk_weighted_assets', 0),
            'Capital_Requirement_USD': final_results.get('capital_requirement', 0),
            'Capital_Efficiency_Pct': (final_results.get('capital_requirement', 0) / 
                                     final_results.get('exposure_at_default', 1)) * 100,
            'Data_Quality_Issues_Count': len(results.get('data_quality_issues', [])),
            'Calculation_Assumptions_Count': len(results.get('assumptions', []))
        }
    
    def _prepare_steps_dataframe(self, calculation_steps: List) -> pd.DataFrame:
        """Prepare calculation steps data for DataFrame."""
        steps_data = []
        for step in calculation_steps:
            step_data = {
                'Step_Number': step.step,
                'Step_Title': step.title,
                'Description': step.description,
                'Formula': step.formula,
                'Result': step.result
            }
            
            # Add thinking insights if available
            if hasattr(step, 'thinking') and step.thinking:
                step_data['Key_Insight'] = step.thinking.get('key_insight', '')
            
            steps_data.append(step_data)
        
        return pd.DataFrame(steps_data)
    
    def _prepare_portfolio_dataframe(self, trades: List, 
                                   collateral: List = None) -> pd.DataFrame:
        """Prepare portfolio data for DataFrame."""
        portfolio_data = []
        
        for trade in trades:
            trade_data = {
                'Trade_ID': trade.trade_id,
                'Counterparty': trade.counterparty,
                'Asset_Class': trade.asset_class.value,
                'Trade_Type': trade.trade_type.value,
                'Notional_USD': trade.notional,
                'Currency': trade.currency,
                'Underlying': trade.underlying,
                'Maturity_Date': trade.maturity_date,
                'Time_to_Maturity_Years': round(trade.time_to_maturity(), 2),
                'MTM_Value_USD': trade.mtm_value,
                'Delta': trade.delta,
                'Central_Clearing_Flag': getattr(trade, 'ceu_flag', 1)
            }
            portfolio_data.append(trade_data)
        
        return pd.DataFrame(portfolio_data)
    
    def _prepare_enhanced_summary_dataframe(self, enhanced_summary: Dict) -> pd.DataFrame:
        """Prepare enhanced summary for DataFrame."""
        summary_items = []
        
        for category, items in enhanced_summary.items():
            for item in items:
                summary_items.append({
                    'Category': category.replace('_', ' ').title(),
                    'Item': item
                })
        
        return pd.DataFrame(summary_items)
    
    def _prepare_data_quality_dataframe(self, data_quality_issues: List) -> pd.DataFrame:
        """Prepare data quality issues for DataFrame."""
        dq_data = []
        
        for issue in data_quality_issues:
            dq_data.append({
                'Field_Name': issue.field_name,
                'Issue_Type': issue.issue_type.value,
                'Impact_Level': issue.impact.value,
                'Current_Value': str(issue.current_value),
                'Recommendation': issue.recommendation,
                'Default_Used': str(issue.default_used) if issue.default_used else ''
            })
        
        return pd.DataFrame(dq_data)
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """Convert objects to JSON-serializable format."""
        if hasattr(obj, '__dict__'):
            return {key: self._make_json_serializable(value) 
                   for key, value in obj.__dict__.items()}
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) 
                   for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif hasattr(obj, 'value'):  # For Enum objects
            return obj.value
        elif hasattr(obj, 'isoformat'):  # For datetime objects
            return obj.isoformat()
        else:
            return obj


# ==============================================================================
# STANDALONE EXPORT FUNCTIONS
# ==============================================================================

def create_summary_csv(results: Dict[str, Any], netting_set_id: str = "unknown") -> str:
    """Create summary CSV export."""
    exporter = SACCRDataExporter()
    return exporter.export_summary_csv(results, netting_set_id)

def create_steps_csv(calculation_steps: List[Dict]) -> str:
    """Create calculation steps CSV export."""
    exporter = SACCRDataExporter()
    return exporter.export_steps_csv(calculation_steps)

def create_portfolio_csv(trades: List, collateral: List = None) -> str:
    """Create portfolio CSV export."""
    exporter = SACCRDataExporter()
    return exporter.export_portfolio_csv(trades, collateral)

def create_excel_workbook(results: Dict[str, Any], trades: List = None, 
                         collateral: List = None, filename: str = None) -> bytes:
    """Create comprehensive Excel workbook."""
    exporter = SACCRDataExporter()
    return exporter.export_excel_workbook(results, trades, collateral, filename)

def create_json_export(results: Dict[str, Any], include_metadata: bool = True) -> str:
    """Create complete JSON export."""
    exporter = SACCRDataExporter()
    return exporter.export_json_complete(results, include_metadata)


# ==============================================================================
# EXPORT UTILITIES
# ==============================================================================

def format_currency(value: float, currency: str = "USD") -> str:
    """Format currency values for export."""
    if abs(value) >= 1_000_000:
        return f"{currency} {value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"{currency} {value/1_000:.1f}K"
    else:
        return f"{currency} {value:.2f}"

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format percentage values for export."""
    return f"{value:.{decimal_places}f}%"

def generate_filename(prefix: str, extension: str, 
                     include_timestamp: bool = True) -> str:
    """Generate standardized filename."""
    timestamp = datetime.now().strftime(FILE_NAMING['timestamp_format'])
    
    if include_timestamp:
        return f"{prefix}_{timestamp}.{extension}"
    else:
        return f"{prefix}.{extension}"

def validate_export_data(results: Dict[str, Any]) -> List[str]:
    """Validate data before export and return any issues."""
    issues = []
    
    if not results:
        issues.append("No results data provided")
        return issues
    
    # Check for required sections
    required_sections = ['final_results', 'calculation_steps']
    for section in required_sections:
        if section not in results:
            issues.append(f"Missing required section: {section}")
    
    # Validate final results
    if 'final_results' in results:
        final_results = results['final_results']
        required_metrics = ['exposure_at_default', 'risk_weighted_assets', 'capital_requirement']
        
        for metric in required_metrics:
            if metric not in final_results:
                issues.append(f"Missing metric in final results: {metric}")
            elif not isinstance(final_results[metric], (int, float)):
                issues.append(f"Invalid data type for {metric}: expected number")
    
    return issues

def compress_large_export(data: Union[str, bytes], threshold_mb: int = 1) -> Union[str, bytes]:
    """Compress export data if it exceeds threshold."""
    import gzip
    
    if isinstance(data, str):
        data_bytes = data.encode('utf-8')
        size_mb = len(data_bytes) / (1024 * 1024)
        
        if size_mb > threshold_mb:
            compressed = gzip.compress(data_bytes)
            return compressed
    
    elif isinstance(data, bytes):
        size_mb = len(data) / (1024 * 1024)
        
        if size_mb > threshold_mb:
            return gzip.compress(data)
    
    return data


# ==============================================================================
# EXPORT TEMPLATES
# ==============================================================================

def create_regulatory_report_template() -> Dict[str, Any]:
    """Create template for regulatory reporting."""
    return {
        'report_header': {
            'institution_name': '[Institution Name]',
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'reporting_period': '[Reporting Period]',
            'regulatory_framework': 'Basel III SA-CCR',
            'calculation_methodology': '24-Step SA-CCR'
        },
        'executive_summary': {
            'total_exposure_at_default': 0,
            'total_risk_weighted_assets': 0,
            'minimum_capital_requirement': 0,
            'number_of_netting_sets': 0,
            'number_of_trades': 0
        },
        'detailed_calculations': [],
        'data_quality_assessment': [],
        'assumptions_and_limitations': [],
        'regulatory_compliance_statement': '[Compliance Statement]'
    }

def create_audit_trail_template() -> Dict[str, Any]:
    """Create template for audit trail documentation."""
    return {
        'calculation_metadata': {
            'calculation_timestamp': datetime.now().isoformat(),
            'application_version': APP_VERSION,
            'methodology_version': 'Basel III SA-CCR',
            'data_sources': [],
            'calculation_parameters': {}
        },
        'input_validation': {
            'validation_rules_applied': [],
            'data_quality_checks': [],
            'missing_data_treatment': []
        },
        'calculation_trail': {
            'step_by_step_results': [],
            'intermediate_calculations': [],
            'formula_applications': []
        },
        'output_validation': {
            'reasonableness_checks': [],
            'benchmark_comparisons': [],
            'sensitivity_analysis': []
        }
    }


def export_calculation_results(results: Dict[str, Any], 
                              format_type: str = "all") -> Dict[str, Any]:
    """
    Export SA-CCR calculation results in specified format(s).
    
    Args:
        results: Complete SA-CCR calculation results
        format_type: Export format - "csv", "excel", "json", or "all"
        
    Returns:
        Dictionary containing export data for each requested format
    """
    exporter = SACCRDataExporter()
    exports = {}
    
    # Extract key information
    netting_set_id = "unknown"
    trades = []
    collateral = []
    
    # Try to extract netting set ID from calculation steps
    if results.get('calculation_steps'):
        step1 = next((s for s in results['calculation_steps'] if s.step == 1), None)
        if step1 and hasattr(step1, 'data'):
            netting_set_id = step1.data.get('netting_set_id', 'unknown')
    
    if format_type in ["csv", "all"]:
        exports['summary_csv'] = exporter.export_summary_csv(results, netting_set_id)
        exports['steps_csv'] = exporter.export_steps_csv(results.get('calculation_steps', []))
        
        # Add portfolio CSV if trade data is available
        if trades:
            exports['portfolio_csv'] = exporter.export_portfolio_csv(trades, collateral)
    
    if format_type in ["excel", "all"]:
        exports['excel_workbook'] = exporter.export_excel_workbook(
            results, trades, collateral
        )
    
    if format_type in ["json", "all"]:
        exports['json_complete'] = exporter.export_json_complete(results, True)
    
    return exports
# ==============================================================================
# USAGE EXAMPLES
# ==============================================================================

"""
Example usage of data export utilities:

# In UI components or calculation handlers:
from utils.data_export import create_summary_csv, create_excel_workbook

# Create CSV export
summary_csv = create_summary_csv(saccr_results, netting_set.netting_set_id)

# Create Excel workbook
excel_data = create_excel_workbook(
    results=saccr_results,
    trades=netting_set.trades,
    collateral=collateral_items
)

# Create JSON export
json_data = create_json_export(saccr_results, include_metadata=True)

# Use in Streamlit download buttons
st.download_button(
    "Download Summary CSV",
    data=summary_csv,
    file_name="saccr_summary.csv",
    mime="text/csv"
)

st.download_button(
    "Download Excel Report", 
    data=excel_data,
    file_name="saccr_analysis.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
"""
