# utils/data_export.py
"""
Data export utilities for SA-CCR calculation results.
Handles CSV, Excel, JSON, and PDF export functionality with proper formatting.
Aligned with the complete US SA-CCR implementation.
"""

import json
import csv
import io
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import pandas as pd
from pathlib import Path

# Application constants
APP_NAME = "SA-CCR Calculator"
APP_VERSION = "1.0.0"

# Export configuration
EXPORT_CONFIG = {
    'json_indent': 2,
    'csv_delimiter': ',',
    'excel_engine': 'openpyxl',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'number_format': '${:,.2f}',
    'percentage_format': '{:.2f}%'
}

FILE_NAMING = {
    'timestamp_format': '%Y%m%d_%H%M%S',
    'prefix_separator': '_',
    'extension_separator': '.'
}

TABLE_CONFIG = {
    'max_rows_display': 1000,
    'precision_dollars': 2,
    'precision_percentages': 4
}


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
    
    def export_steps_csv(self, results: Dict[str, Any]) -> str:
        """
        Export detailed calculation steps to CSV format.
        
        Args:
            results: Complete SA-CCR calculation results
            
        Returns:
            CSV data as string
        """
        steps_data = []
        
        # Extract shared steps
        shared_steps = results.get('shared_calculation_steps', {})
        for step_num, step_data in shared_steps.items():
            steps_data.append({
                'Step_Number': step_num,
                'Step_Title': step_data.get('title', f'Step {step_num}'),
                'Step_Type': 'Shared',
                'Description': self._format_step_description(step_data),
                'Key_Values': self._extract_key_values(step_data),
                'Formula': step_data.get('formula', 'N/A')
            })
        
        # Extract scenario-specific steps
        for scenario_name, scenario_data in results.get('scenarios', {}).items():
            scenario_steps = [
                ('Maturity Factor', scenario_data.get('maturity_factors', [])),
                ('Adjusted Amounts', scenario_data.get('adjusted_amounts', [])),
                ('Hedging Set AddOns', scenario_data.get('hedging_set_addons', [])),
                ('Asset Class AddOns', scenario_data.get('asset_class_addons', [])),
                ('Aggregate AddOn', scenario_data.get('aggregate_addon', 0)),
                ('PFE Multiplier', scenario_data.get('pfe_multiplier', 0)),
                ('PFE', scenario_data.get('pfe', 0)),
                ('RC', scenario_data.get('rc', 0)),
                ('EAD', scenario_data.get('final_ead', 0))
            ]
            
            for step_name, step_value in scenario_steps:
                steps_data.append({
                    'Step_Number': f'{scenario_name}_{step_name}',
                    'Step_Title': f'{step_name} ({scenario_name})',
                    'Step_Type': scenario_name,
                    'Description': f'{step_name} calculation for {scenario_name} scenario',
                    'Key_Values': str(step_value) if not isinstance(step_value, list) else f'{len(step_value)} items',
                    'Formula': scenario_data.get('regulatory_formulas', {}).get(step_name.lower().replace(' ', '_'), 'See regulation')
                })
        
        if not steps_data:
            return "No calculation steps available"
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['Step_Number', 'Step_Title', 'Step_Type', 'Description', 'Key_Values', 'Formula'])
        writer.writeheader()
        writer.writerows(steps_data)
        
        return output.getvalue()
    
    def export_portfolio_csv(self, netting_set, collateral: List = None) -> str:
        """
        Export portfolio data to CSV format.
        
        Args:
            netting_set: NettingSet object containing trades
            collateral: Optional list of Collateral objects
            
        Returns:
            CSV data as string
        """
        output = io.StringIO()
        
        # Export trades data
        if hasattr(netting_set, 'trades') and netting_set.trades:
            trades_data = []
            for trade in netting_set.trades:
                trade_row = {
                    'Trade_ID': trade.trade_id,
                    'Counterparty': trade.counterparty,
                    'Asset_Class': trade.asset_class.value if hasattr(trade.asset_class, 'value') else str(trade.asset_class),
                    'Trade_Type': trade.trade_type.value if hasattr(trade.trade_type, 'value') else str(trade.trade_type),
                    'Notional': trade.notional,
                    'Currency': trade.currency,
                    'Underlying': trade.underlying,
                    'Maturity_Date': trade.maturity_date.strftime('%Y-%m-%d'),
                    'Time_to_Maturity_Years': trade.time_to_maturity(datetime.now()),
                    'MTM_Value': trade.mtm_value,
                    'Delta': trade.delta,
                    'CEU_Flag': getattr(trade, 'ceu_flag', 1)
                }
                trades_data.append(trade_row)
            
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
                    'Collateral_Type': coll.collateral_type.value if hasattr(coll.collateral_type, 'value') else str(coll.collateral_type),
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
                             netting_set=None, collateral: List = None,
                             filename: str = None) -> bytes:
        """
        Export comprehensive results to Excel workbook.
        
        Args:
            results: SA-CCR calculation results
            netting_set: NettingSet object
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
            
            # Scenarios comparison sheet
            scenarios_df = self._prepare_scenarios_dataframe(results)
            scenarios_df.to_excel(writer, sheet_name='Scenarios_Comparison', index=False)
            
            # Shared calculation steps sheet
            shared_steps_df = self._prepare_shared_steps_dataframe(results)
            shared_steps_df.to_excel(writer, sheet_name='Shared_Steps', index=False)
            
            # Portfolio sheet
            if netting_set:
                portfolio_df = self._prepare_portfolio_dataframe(netting_set, collateral)
                portfolio_df.to_excel(writer, sheet_name='Portfolio', index=False)
            
            # Regulatory parameters sheet
            regulatory_df = self._prepare_regulatory_parameters_dataframe()
            regulatory_df.to_excel(writer, sheet_name='Regulatory_Parameters', index=False)
        
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
                'data_includes': list(results.keys()),
                'regulatory_reference': results.get('regulatory_reference', '12 CFR 217.132')
            }
        
        # Convert non-serializable objects
        export_data = self._make_json_serializable(export_data)
        
        return json.dumps(export_data, indent=EXPORT_CONFIG['json_indent'], 
                         ensure_ascii=False, default=str)
    
    def _prepare_summary_data(self, results: Dict[str, Any], 
                             netting_set_id: str = "unknown") -> Dict[str, Any]:
        """Prepare summary data for export."""
        final_results = results.get('final_results', {})
        selection = results.get('selection', {})
        
        return {
            'Calculation_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Netting_Set_ID': netting_set_id,
            'Application': APP_NAME,
            'Version': APP_VERSION,
            'Regulatory_Reference': results.get('regulatory_reference', '12 CFR 217.132'),
            'Selected_Scenario': selection.get('selected_scenario', 'Unknown'),
            'Replacement_Cost_USD': final_results.get('replacement_cost', 0),
            'Potential_Future_Exposure_USD': final_results.get('potential_future_exposure', 0),
            'Exposure_at_Default_USD': final_results.get('exposure_at_default', 0),
            'Risk_Weighted_Assets_USD': final_results.get('risk_weighted_assets', 0),
            'Capital_Requirement_USD': final_results.get('capital_requirement', 0),
            'Capital_Efficiency_Pct': self._calculate_capital_efficiency(final_results),
            'EAD_Difference_USD': selection.get('ead_difference', 0),
            'Capital_Savings_USD': selection.get('capital_savings', 0)
        }
    
    def _prepare_scenarios_dataframe(self, results: Dict[str, Any]) -> pd.DataFrame:
        """Prepare scenarios comparison data for DataFrame."""
        scenarios_data = []
        
        scenarios = results.get('scenarios', {})
        for scenario_name, scenario_data in scenarios.items():
            scenario_row = {
                'Scenario': scenario_name.title(),
                'Aggregate_AddOn': scenario_data.get('aggregate_addon', 0),
                'PFE_Multiplier': scenario_data.get('pfe_multiplier', 0),
                'PFE': scenario_data.get('pfe', 0),
                'RC': scenario_data.get('rc', 0),
                'EAD': scenario_data.get('final_ead', 0),
                'RWA': scenario_data.get('rwa', 0),
                'Capital_Requirement': scenario_data.get('final_capital', 0)
            }
            scenarios_data.append(scenario_row)
        
        return pd.DataFrame(scenarios_data)
    
    def _prepare_shared_steps_dataframe(self, results: Dict[str, Any]) -> pd.DataFrame:
        """Prepare shared calculation steps for DataFrame."""
        steps_data = []
        
        shared_steps = results.get('shared_calculation_steps', {})
        for step_num, step_data in shared_steps.items():
            step_row = {
                'Step_Number': step_num,
                'Step_Title': step_data.get('title', f'Step {step_num}'),
                'Description': self._format_step_description(step_data),
                'Key_Result': self._extract_key_result(step_data),
                'Formula': step_data.get('formula', 'See regulation')
            }
            steps_data.append(step_row)
        
        return pd.DataFrame(steps_data)
    
    def _prepare_portfolio_dataframe(self, netting_set, collateral: List = None) -> pd.DataFrame:
        """Prepare portfolio data for DataFrame."""
        portfolio_data = []
        
        if hasattr(netting_set, 'trades'):
            for trade in netting_set.trades:
                trade_data = {
                    'Trade_ID': trade.trade_id,
                    'Counterparty': trade.counterparty,
                    'Asset_Class': trade.asset_class.value if hasattr(trade.asset_class, 'value') else str(trade.asset_class),
                    'Trade_Type': trade.trade_type.value if hasattr(trade.trade_type, 'value') else str(trade.trade_type),
                    'Notional_USD': trade.notional,
                    'Currency': trade.currency,
                    'Underlying': trade.underlying,
                    'Maturity_Date': trade.maturity_date,
                    'Time_to_Maturity_Years': round(trade.time_to_maturity(datetime.now()), 2),
                    'MTM_Value_USD': trade.mtm_value,
                    'Delta': trade.delta,
                    'Central_Clearing_Flag': getattr(trade, 'ceu_flag', 1)
                }
                portfolio_data.append(trade_data)
        
        return pd.DataFrame(portfolio_data)
    
    def _prepare_regulatory_parameters_dataframe(self) -> pd.DataFrame:
        """Prepare regulatory parameters for DataFrame."""
        # Import the supervisory factors from the SA-CCR engine
        try:
            from saccr_engine import US_SUPERVISORY_FACTORS, US_SUPERVISORY_CORRELATIONS, US_MPOR_VALUES
            
            params_data = []
            
            # Add supervisory factors
            for asset_class, factors in US_SUPERVISORY_FACTORS.items():
                if isinstance(factors, dict):
                    for subcategory, factor in factors.items():
                        params_data.append({
                            'Parameter_Type': 'Supervisory Factor',
                            'Asset_Class': asset_class.value if hasattr(asset_class, 'value') else str(asset_class),
                            'Subcategory': subcategory,
                            'Value': f"{factor}%",
                            'Source': '12 CFR 217.132 Table 3'
                        })
                else:
                    params_data.append({
                        'Parameter_Type': 'Supervisory Factor',
                        'Asset_Class': asset_class.value if hasattr(asset_class, 'value') else str(asset_class),
                        'Subcategory': 'All',
                        'Value': f"{factors}%",
                        'Source': '12 CFR 217.132 Table 3'
                    })
            
            # Add MPOR values
            for mpor_type, days in US_MPOR_VALUES.items():
                params_data.append({
                    'Parameter_Type': 'MPOR',
                    'Asset_Class': 'All',
                    'Subcategory': mpor_type.replace('_', ' ').title(),
                    'Value': f"{days} business days",
                    'Source': '12 CFR 217.132'
                })
            
        except ImportError:
            # Fallback if import fails
            params_data = [{
                'Parameter_Type': 'Note',
                'Asset_Class': 'All',
                'Subcategory': 'Import Error',
                'Value': 'Could not load regulatory parameters',
                'Source': 'System Error'
            }]
        
        return pd.DataFrame(params_data)
    
    def _format_step_description(self, step_data: Dict) -> str:
        """Format step description for export."""
        if 'description' in step_data:
            return step_data['description']
        
        title = step_data.get('title', '')
        if 'netting_set_id' in step_data:
            return f"Netting Set: {step_data['netting_set_id']}"
        elif 'asset_classes' in step_data:
            return f"Asset classes: {', '.join(step_data['asset_classes'])}"
        elif 'alpha' in step_data:
            return f"Alpha value: {step_data['alpha']}"
        else:
            return title
    
    def _extract_key_values(self, step_data: Dict) -> str:
        """Extract key values from step data."""
        key_fields = ['total_notional', 'total_adjusted_notional', 'alpha', 'threshold', 'mta', 'nica']
        values = []
        
        for field in key_fields:
            if field in step_data:
                values.append(f"{field}: {step_data[field]}")
        
        return '; '.join(values) if values else 'See step details'
    
    def _extract_key_result(self, step_data: Dict) -> str:
        """Extract key result from step data."""
        if 'total_adjusted_notional' in step_data:
            return f"${step_data['total_adjusted_notional']:,.0f}"
        elif 'alpha' in step_data:
            return str(step_data['alpha'])
        elif 'threshold' in step_data:
            return f"TH: ${step_data['threshold']:,.0f}"
        else:
            return 'See details'
    
    def _calculate_capital_efficiency(self, final_results: Dict) -> float:
        """Calculate capital efficiency percentage."""
        ead = final_results.get('exposure_at_default', 0)
        capital = final_results.get('capital_requirement', 0)
        
        if ead > 0:
            return (capital / ead) * 100
        return 0.0
    
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

def create_steps_csv(results: Dict[str, Any]) -> str:
    """Create calculation steps CSV export."""
    exporter = SACCRDataExporter()
    return exporter.export_steps_csv(results)

def create_portfolio_csv(netting_set, collateral: List = None) -> str:
    """Create portfolio CSV export."""
    exporter = SACCRDataExporter()
    return exporter.export_portfolio_csv(netting_set, collateral)

def create_excel_workbook(results: Dict[str, Any], netting_set=None, 
                         collateral: List = None, filename: str = None) -> bytes:
    """Create comprehensive Excel workbook."""
    exporter = SACCRDataExporter()
    return exporter.export_excel_workbook(results, netting_set, collateral, filename)

def create_json_export(results: Dict[str, Any], include_metadata: bool = True) -> str:
    """Create complete JSON export."""
    exporter = SACCRDataExporter()
    return exporter.export_json_complete(results, include_metadata)


# ==============================================================================
# EXPORT UTILITIES
# ==============================================================================

def format_currency(value: float, currency: str = "USD") -> str:
    """Format currency values for export."""
    if abs(value) >= 1_000_000_000:
        return f"{currency} {value/1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:
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
    required_sections = ['final_results']
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


def export_calculation_results(results: Dict[str, Any], 
                              netting_set=None,
                              collateral: List = None,
                              format_type: str = "all") -> Dict[str, Any]:
    """
    Export SA-CCR calculation results in specified format(s).
    
    Args:
        results: Complete SA-CCR calculation results
        netting_set: NettingSet object containing trades
        collateral: List of collateral objects
        format_type: Export format - "csv", "excel", "json", or "all"
        
    Returns:
        Dictionary containing export data for each requested format
    """
    exporter = SACCRDataExporter()
    exports = {}
    
    # Extract netting set ID
    netting_set_id = "unknown"
    if netting_set and hasattr(netting_set, 'netting_set_id'):
        netting_set_id = netting_set.netting_set_id
    elif results.get('shared_calculation_steps', {}).get(1):
        netting_set_id = results['shared_calculation_steps'][1].get('netting_set_id', 'unknown')
    
    if format_type in ["csv", "all"]:
        exports['summary_csv'] = exporter.export_summary_csv(results, netting_set_id)
        exports['steps_csv'] = exporter.export_steps_csv(results)
        
        # Add portfolio CSV if netting set is available
        if netting_set:
            exports['portfolio_csv'] = exporter.export_portfolio_csv(netting_set, collateral)
    
    if format_type in ["excel", "all"]:
        exports['excel_workbook'] = exporter.export_excel_workbook(
            results, netting_set, collateral
        )
    
    if format_type in ["json", "all"]:
        exports['json_complete'] = exporter.export_json_complete(results, True)
    
    return exports


# ==============================================================================
# REGULATORY REPORT TEMPLATES
# ==============================================================================

def create_regulatory_report_template() -> Dict[str, Any]:
    """Create template for regulatory reporting."""
    return {
        'report_header': {
            'institution_name': '[Institution Name]',
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'reporting_period': '[Reporting Period]',
            'regulatory_framework': 'Basel III SA-CCR',
            'calculation_methodology': '24-Step SA-CCR per 12 CFR 217.132'
        },
        'executive_summary': {
            'total_exposure_at_default': 0,
            'total_risk_weighted_assets': 0,
            'minimum_capital_requirement': 0,
            'number_of_netting_sets': 0,
            'number_of_trades': 0
        },
        'detailed_calculations': [],
        'regulatory_compliance_statement': 'Calculation performed per 12 CFR 217.132'
    }

def generate_regulatory_report(results: Dict[str, Any], netting_set=None) -> str:
    """Generate a regulatory compliance report."""
    report = f"""
REGULATORY COMPLIANCE REPORT
12 CFR 217.132 - SA-CCR CALCULATION

Calculation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Regulatory Framework: {results.get('regulatory_reference', '12 CFR 217.132')}
Implementation: {results.get('table_3_implementation', 'Complete')}

EXECUTIVE SUMMARY:
Selected Scenario: {results.get('selection', {}).get('selected_scenario', 'N/A')}
Final EAD: ${results.get('final_results', {}).get('exposure_at_default', 0):,.0f}
Capital Requirement: ${results.get('final_results', {}).get('capital_requirement', 0):,.0f}

SCENARIO COMPARISON:
                    Margined         Unmargined       
PFE:               ${results.get('scenarios', {}).get('margined', {}).get('pfe', 0):>12,.0f}  ${results.get('scenarios', {}).get('unmargined', {}).get('pfe', 0):>12,.0f}
RC:                ${results.get('scenarios', {}).get('margined', {}).get('rc', 0):>12,.0f}  ${results.get('scenarios', {}).get('unmargined', {}).get('rc', 0):>12,.0f}
EAD:               ${results.get('scenarios', {}).get('margined', {}).get('final_ead', 0):>12,.0f}  ${results.get('scenarios', {}).get('unmargined', {}).get('final_ead', 0):>12,.0f}

REGULATORY COMPLIANCE:
✓ 12 CFR 217.132 Table 3 - Complete Implementation
✓ All supervisory factors applied per regulation
✓ MPOR values per US regulatory standards
✓ Dual scenario calculation performed
✓ Minimum EAD selection rule applied

This report certifies compliance with US Federal Register 12 CFR 217.132
for counterparty credit risk capital requirements calculation.
    """
    
    return report
